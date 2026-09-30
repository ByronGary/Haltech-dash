# RealDash setup

Settings that other Haltech users report as working. Adjust the adapter line to whichever adapter you bought.

## 1. Load the CAN description file

Copy `can/haltech_v3_can.xml` onto the head unit (USB stick, Google Drive, or `adb push`).
RealDash also ships a built-in **Haltech CAN V2** description; the XML in this repo is the same protocol with
more channels exposed, and it is what you edit when you want a channel the built-in one lacks.

## 2. Create the connection

Garage -> open the car door -> tap the instrument cluster -> **Add connection**:

| Setting | Value |
|---------|-------|
| Category | Adapters (CAN/LIN) |
| Adapter | CAN Analyzer (Type 1) for Seeed, or Waveshare USB-CAN-A |
| Interface | Serial/USB, pick the device that appears (CH340 / QinHeng) |
| Serial baud | **1228800** |
| CAN description file | `haltech_v3_can.xml` (or built-in Haltech CAN V2) |
| CAN speed | **1000 kbps** |
| CAN frame | Standard (11-bit) |
| CAN mode | Normal |

For the Waveshare, one user needed, in the Waveshare Windows configuration tool, **Protocol = variable length**
and **only send once** enabled before RealDash would receive data. Apply those with the adapter on a PC first.

## 3. Verify

- Settings -> **CAN Monitor** shows frames 0x360, 0x361, 0x362 at ~50 Hz and 0x3E0 at ~5 Hz when the ECU is
  powered. If the monitor is empty, see `troubleshooting.md`.
- Add a text gauge for RPM (targetId 37) and Coolant Temperature (targetId 14) and confirm they move.

## 4. Units

RealDash converts internally. The XML tags temperatures as Kelvin (`units="K"`), so set
Settings -> Units & Values to Fahrenheit/psi/mph and every gauge follows.

## 5. Bench testing without the car

On a laptop on the same Wi-Fi as the head unit:

```
python3 tools/haltech_sim.py            # listens on 0.0.0.0:35000
```

In RealDash create a second connection: **RealDash CAN -> TCP/IP**, IP = the laptop's LAN address, port 35000,
CAN description file = `can/haltech_v3_can.xml`. Disable it again before going to the car.

To replay a real log captured with CAN Monitor instead:

```
python3 tools/canplayback.py rdcan_YYYY-MM-DD_hh-mm-ss.csv 35000
```
