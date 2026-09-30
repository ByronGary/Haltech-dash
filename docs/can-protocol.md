# Haltech CAN broadcast protocol V2, as used by `can/haltech_v3_can.xml`

Bus: 1 Mbit/s, 11-bit standard IDs, all multi-byte values **big-endian unsigned 16-bit** unless noted.
Temperatures are in 0.1 K. Pressures are 0.1 kPa **absolute**; the XML subtracts 101.3 to show gauge pressure
for coolant, fuel, oil and wastegate. Lambda is 0.001. Full detail is in
`reference/Haltech-CAN-Broadcast-Protocol-V2.35.0.pdf`.

The "RealDash" column is the `targetId` the XML maps to. `name` means a custom "Haltech: ..." input in the
ECU Specific category.

## 50 Hz

| ID | Bytes | Channel | Scale | RealDash |
|----|-------|---------|-------|----------|
| 0x360 | 0-1 | RPM | x1 | 37 RPM |
| 0x360 | 2-3 | MAP | /10 kPa | 31 MAP |
| 0x360 | 4-5 | TPS | /10 % | 42 Throttle |
| 0x360 | 6-7 | Coolant pressure | /10 - 101.3 kPa | 759 |
| 0x361 | 0-1 | Fuel pressure | /10 - 101.3 kPa | 202 |
| 0x361 | 2-3 | Oil pressure | /10 - 101.3 kPa | 151 |
| 0x361 | 4-5 | Engine demand | /10 % | name |
| 0x361 | 6-7 | Wastegate pressure | /10 - 101.3 kPa | name |
| 0x362 | 0-1 | Injector duty stage 1 | /10 % | 119 |
| 0x362 | 2-3 | Injector duty stage 2 | /10 % | 120 |
| 0x362 | 4-5 | Ignition angle leading | /10 deg | 38 Spark advance |
| 0x362 | 6-7 | Ignition angle trailing | /10 deg | (v2 XML only) |
| 0x363 | 0-1 / 2-3 | Wheel slip / wheel diff | /10 km/h | name |
| 0x364 | 0-7 | Injection stage 1-4 avg time | /1000 ms | name |

## 20 Hz

| ID | Bytes | Channel | Scale | RealDash |
|----|-------|---------|-------|----------|
| 0x368 | 0-1, 2-3 | Lambda 1, Lambda 2 | /1000 | 254, 255 |
| 0x368 | 4-5, 6-7 | Lambda 3, Lambda 4 | /1000 | name |
| 0x369 | 0-7 | Trigger error / trigger / home counters, sync level | x1 | name |
| 0x36A | 0-1, 2-3 | Knock level 1, 2 | /100 dB | name |
| 0x36C | 0-7 | Wheel speed FL, FR, RL, RR | /10 km/h | name |
| 0x36D | 4-5, 6-7 | Exhaust cam angle 1, 2 | /10 deg | 493, 495 |
| 0x36E | 1 bit0 | Engine limiting active | bit | name |
| 0x36E | 2-3, 4-5 | Launch control ignition retard / fuel enrich | /10 | name |
| 0x36F | 0-1, 2-3 | Generic output 1 duty, boost control output | /10 % | name |
| 0x370 | 0-1 | Vehicle speed | /10 km/h | 81 |
| 0x370 | 4-5, 6-7 | Intake cam angle 1, 2 | /10 deg | 492, 494 |
| 0x371 | 0-1, 2-3 | Fuel flow, fuel flow return | cc/min | 490, name |

## 10 Hz

| ID | Bytes | Channel | Scale | RealDash |
|----|-------|---------|-------|----------|
| 0x372 | 0-1 | Battery voltage | /10 V | 12 |
| 0x372 | 4-5 | Target boost | /10 kPa | 270 |
| 0x372 | 6-7 | Barometric pressure | /10 kPa | 11 |
| 0x373 - 0x375 | 0-7 | EGT 1-12 | /10 K | not mapped in v3 XML; add if you run EGTs |

## 5 Hz

| ID | Bytes | Channel | Scale | RealDash |
|----|-------|---------|-------|----------|
| 0x3E0 | 0-1 | Coolant temp | /10 K | 14 |
| 0x3E0 | 2-3 | Intake air temp | /10 K | 27 |
| 0x3E0 | 4-5 | Fuel temp | /10 K | 499 |
| 0x3E0 | 6-7 | Oil temp | /10 K | 152 |
| 0x3E1 | 0-1 | Gearbox oil temp | /10 K | 138 |
| 0x3E1 | 2-3 | Diff oil temp | /10 K | name |
| 0x3E1 | 4-5 | Fuel composition (ethanol %) | /10 % | name |
| 0x3E2 | 0-1 | Fuel level | /10 L | name |
| 0x3E3 | 0-7 | Short term trim bank 1, 2 / long term trim bank 1, 2 | /10 %, **signed** | 17, 18, 102, 104 |
| 0x3E4 | bits | Status bits: oil light, clutch, brake, overrun, reverse, neutral, launch, fans, A/C, traction, park brake, battery light, CEL | bit | mixed, see XML |
| 0x3E4 | 4, 5, 6 | Rotary trim pot 1-3 | x1 | name |
| 0x3E5 | 6-7 | Driveshaft RPM | x1 | name |
| 0x3E9 | 4-5 | Lambda target | /1000 | 256 |
| 0x3EB | 4-5, 6-7 | Ignition angle bank 1, bank 2 | /10 deg | 38, name |

## Slow / status

| ID | Bytes | Channel | Scale | RealDash |
|----|-------|---------|-------|----------|
| 0x469 | 0-1 | ECU temperature | /10 K | name |
| 0x470 | 0-1, 2-3, 4-5 | Wideband overall, bank 1, bank 2 | /1000 | name |
| 0x470 | 6 | Gear selector position | x1 | name |
| 0x470 | 7 | **Gear** | enum 0=N,1..6 | name "Haltech: Gear" |
| 0x471 | 0-1 | Injector pressure differential | /10 kPa | name |
| 0x471 | 2-3 | Accelerator pedal position | /10 % | name |
| 0x471 | 4-5 | Exhaust manifold pressure | /10 kPa | name |
| 0x473 | bits | Cut method, antilag / traction switch states, fuel pump 1-4 | bit/enum | 182-185, name |
| 0x477 | 0-1 | RPM limit | x1 | 271 |
| 0x477 | 2-7 | Cut %, limiter function/method enums | mixed | name |
| 0x6F7 | 3 bits | Generic outputs 1-8 | bit | name |

## Frames RealDash writes to the ECU (IO Box emulation)

`0x2C0`, `0x2C2`, `0x2C4` are transmitted by RealDash every 100 ms to emulate a Haltech IO Box A, so RealDash
buttons can feed AVI1-4 analog values (0-4095) and DPI1-4 duty inputs into the ECU. Leave them alone unless you
intend to drive ECU inputs from the screen, and never enable a second IO Box A on the same bus.

## Things worth adding to the XML later

- Map the gear byte (0x470 byte 7) to `targetId="139"` (Transmission -> Gear) instead of a custom name so the
  stock RealDash gear gauges work.
- Map EGTs (0x373) if the car has them.
- `timeout` on the 0x360 frame so gauges drop to zero when the ECU goes off.
