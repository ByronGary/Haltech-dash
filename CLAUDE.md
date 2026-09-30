# Haltech-Dash

RealDash dashboard for a Haltech Elite 2500 on an ATOTO S8 Gen2 Standard Android head unit,
connected through a USB CAN adapter. No trading code here; this is an automotive project.

## Facts that are easy to get wrong

- Haltech CAN broadcast: **1 Mbit/s, 11-bit standard IDs, big-endian**, temperatures in **0.1 K**,
  pressures in 0.1 kPa **absolute** (subtract 101.3 for gauge). See `docs/can-protocol.md`.
- The ECU only broadcasts on a connector if NSP's *Haltech CAN System -> Bus Selection* includes it.
  "Both Main and Aux" is the safe setting.
- RealDash serial/USB baud for the Seeed/Waveshare style USB-CAN analyzer is **1228800**, not 115200.
- The canonical XML is `can/haltech_v3_can.xml`. It came from the public-domain RealDash-extras repo;
  do not re-download over it without re-applying the `tragetId` -> `targetId` fix on the brake-pedal bit.
- `tools/haltech_sim.py` speaks the RealDash CAN "44" frame (4-byte tag, 4-byte little-endian ID,
  8-byte payload) over TCP. It is for bench testing only.

## Conventions

- Docs in `docs/`, dashboards exported from RealDash go in `dashboards/` as `.rd` files.
- Keep everything stdlib Python; the tools must run on any laptop with no installs.
- When adding a value to the XML, prefer a RealDash `targetId` over a custom `name` so stock gauges work.
- Do not use em dashes in files. Use hyphens.
