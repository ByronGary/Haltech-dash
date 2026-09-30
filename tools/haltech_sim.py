#!/usr/bin/env python3
"""
haltech_sim.py - bench simulator for the Haltech V2 CAN broadcast.

Serves synthetic Haltech Elite frames over TCP in the RealDash CAN "44" frame format, so a RealDash
dashboard can be built and tested on the head unit before the car is wired.

    RealDash CAN '44' frame:
      4 bytes  0x44 0x33 0x22 0x11
      4 bytes  CAN id, 32-bit little endian
      8 bytes  payload (padded with zeros)

Usage:
    python3 tools/haltech_sim.py [--host 0.0.0.0] [--port 35000] [--speed 1.0]

Then in RealDash: Garage -> cluster -> Add connection -> RealDash CAN -> TCP/IP,
IP = this machine's LAN address, port = 35000, description file = can/haltech_v3_can.xml.

Stdlib only. Payload layouts follow can/haltech_v3_can.xml (big-endian, temps in 0.1 K,
pressures in 0.1 kPa absolute, lambda in 0.001).
"""

import argparse
import math
import socket
import struct
import time

TAG = bytes([0x44, 0x33, 0x22, 0x11])
KELVIN = 273.15
BARO_KPA = 101.3


def frame(can_id: int, payload: bytes) -> bytes:
    payload = payload[:8].ljust(8, b"\x00")
    return TAG + struct.pack("<I", can_id) + payload


def u16(*vals) -> bytes:
    return b"".join(struct.pack(">H", max(0, min(65535, int(round(v))))) for v in vals)


def s16(*vals) -> bytes:
    return b"".join(struct.pack(">h", max(-32768, min(32767, int(round(v))))) for v in vals)


class Engine:
    """A crude but plausible drive cycle: idle, pull through the gears, cruise, decel, repeat."""

    GEAR_RATIOS = [0.0, 3.6, 2.2, 1.5, 1.1, 0.87, 0.72]  # index = gear, 0 = neutral
    FINAL = 3.9
    TYRE_CIRC_M = 1.95
    REDLINE = 7000

    def __init__(self):
        self.t0 = time.monotonic()
        self.rpm = 900.0
        self.gear = 0
        self.tps = 0.0
        self.speed = 0.0
        self.clt_c = 22.0
        self.brake = False
        self.clutch = False

    def step(self, t: float) -> None:
        cycle = t % 60.0
        if cycle < 5:                                   # idle
            self.gear, self.tps, target = 0, 2.0, 900
        elif cycle < 35:                                # accelerate through gears
            phase = (cycle - 5) / 30.0
            self.gear = min(6, 1 + int(phase * 6))
            self.tps = 85.0
            target = 2500 + 4300 * ((phase * 6) % 1.0)
        elif cycle < 45:                                # cruise
            self.gear, self.tps, target = 6, 18.0, 3200
        else:                                           # decel to stop
            self.gear = max(1, 6 - int((cycle - 45) / 2.5))
            self.tps, target = 0.0, 1200
        self.rpm += (target - self.rpm) * 0.15 + 25 * math.sin(t * 9)
        self.rpm = max(850, min(self.REDLINE, self.rpm))
        if self.gear:
            wheel_rps = self.rpm / 60 / (self.GEAR_RATIOS[self.gear] * self.FINAL)
            self.speed = wheel_rps * self.TYRE_CIRC_M * 3.6
        else:
            self.speed = 0.0
        self.brake = cycle >= 45
        self.clutch = 5 <= cycle < 35 and ((cycle - 5) * 6 / 30.0) % 1.0 < 0.08
        self.clt_c = min(92.0, 22.0 + t * 0.6)         # warms up over ~2 min

    # --- frame builders -------------------------------------------------
    def map_kpa(self) -> float:
        boost = max(0.0, (self.tps - 40) / 60) * (self.rpm / self.REDLINE) * 110
        return 30 + self.tps * 0.7 + boost

    def f_360(self):
        return u16(self.rpm, self.map_kpa() * 10, self.tps * 10, (BARO_KPA + 95) * 10)

    def f_361(self):
        fuel = BARO_KPA + 300 + max(0.0, self.map_kpa() - BARO_KPA)
        oil = BARO_KPA + 120 + self.rpm / 25
        return u16(fuel * 10, oil * 10, self.tps * 10, (BARO_KPA + max(0.0, self.map_kpa() - BARO_KPA) * 0.6) * 10)

    def f_362(self):
        duty = self.rpm / self.REDLINE * self.tps * 0.9
        ign = 32 - (self.map_kpa() - 30) * 0.12 + self.rpm / 700
        return u16(duty * 10, 0, ign * 10, ign * 10)

    def f_368(self):
        lam = 0.98 - (self.tps / 100) * 0.18 + 0.01 * math.sin(self.rpm / 300)
        return u16(lam * 1000, (lam + 0.01) * 1000, 0, 0)

    def f_370(self):
        return u16(self.speed * 10, 0, 12 + self.tps * 0.2, 12 + self.tps * 0.2)

    def f_372(self):
        volts = 13.9 + (0.3 if self.rpm > 1200 else -0.6)
        return u16(volts * 10, 0, (BARO_KPA + 100) * 10, BARO_KPA * 10)

    def f_3e0(self):
        iat = 28 + self.map_kpa() * 0.08
        return u16((self.clt_c + KELVIN) * 10, (iat + KELVIN) * 10, (34 + KELVIN) * 10, (self.clt_c + 6 + KELVIN) * 10)

    def f_3e1(self):
        return u16((self.clt_c - 5 + KELVIN) * 10, (60 + KELVIN) * 10, 100, 0)

    def f_3e2(self):
        return u16(48.5 * 10)

    def f_3e3(self):
        st = 3.0 * math.sin(self.rpm / 500)
        return s16(st * 10, -st * 10, 1.5 * 10, -0.8 * 10)

    def f_3e4(self):
        b = bytearray(8)
        b[1] |= (1 << 1) if self.clutch else 0            # clutch switch
        b[1] |= (1 << 2) if self.brake else 0             # brake pedal
        b[1] |= (1 << 4) if self.tps == 0 and self.rpm > 1500 else 0   # overrun
        b[1] |= (1 << 7) if self.gear == 0 else 0         # neutral
        b[3] |= (1 << 0) if self.clt_c > 88 else 0        # thermofan 1
        b[7] |= (1 << 7) if self.rpm > 6800 else 0        # check engine light at the limiter
        return bytes(b)

    def f_470(self):
        lam = 0.98 - (self.tps / 100) * 0.18
        return u16(lam * 1000, lam * 1000, (lam + 0.01) * 1000) + bytes([self.gear, self.gear])

    def f_477(self):
        return u16(self.REDLINE, 0) + bytes([0, 0, 0, 0])


def serve(host: str, port: int, speed: float) -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(2)
    print(f"haltech_sim listening on {host}:{port}  (LAN ip: {lan_ip()})")
    print("RealDash: RealDash CAN -> TCP/IP -> this address, XML = can/haltech_v3_can.xml")
    while True:
        conn, addr = srv.accept()
        print("client", addr)
        try:
            stream(conn, speed)
        except (BrokenPipeError, ConnectionResetError):
            print("client gone", addr)
        finally:
            conn.close()


def stream(conn: socket.socket, speed: float) -> None:
    eng = Engine()
    tick = 0
    period = 0.02  # 50 Hz base rate
    while True:
        t = (time.monotonic() - eng.t0) * speed
        eng.step(t)
        out = [frame(0x360, eng.f_360()), frame(0x361, eng.f_361()), frame(0x362, eng.f_362())]
        if tick % 2 == 0:                                            # ~25 Hz
            out += [frame(0x368, eng.f_368()), frame(0x370, eng.f_370())]
        if tick % 5 == 0:                                            # 10 Hz
            out.append(frame(0x372, eng.f_372()))
        if tick % 10 == 0:                                           # 5 Hz
            out += [frame(0x3E0, eng.f_3e0()), frame(0x3E1, eng.f_3e1()), frame(0x3E2, eng.f_3e2()),
                    frame(0x3E3, eng.f_3e3()), frame(0x3E4, eng.f_3e4())]
        if tick % 25 == 0:                                           # 2 Hz
            out += [frame(0x470, eng.f_470()), frame(0x477, eng.f_477())]
        conn.sendall(b"".join(out))
        tick += 1
        time.sleep(period)


def lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "?"
    finally:
        s.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=35000)
    ap.add_argument("--speed", type=float, default=1.0, help="drive-cycle time multiplier")
    a = ap.parse_args()
    try:
        serve(a.host, a.port, a.speed)
    except KeyboardInterrupt:
        pass
