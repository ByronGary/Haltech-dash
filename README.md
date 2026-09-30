# Haltech-Dash

A RealDash dashboard for a **Haltech Elite 2500** ECU, displayed on an
**ATOTO S8 Gen2 Standard** Android head unit, fed by a **USB CAN adapter**
plugged into the head unit's USB host port.

```
Haltech Elite 2500 ──CAN (1 Mbit, 11-bit IDs)──> USB-CAN adapter ──USB OTG──> ATOTO S8 Gen2 (RealDash)
```

## Repo layout

| Path | What it is |
|------|------------|
| `can/haltech_v3_can.xml` | RealDash CAN description for the Haltech V2 broadcast protocol. Copied from the official RealDash-extras repo (public domain), with one upstream typo fixed. Load this in RealDash, or start from it when customising. |
| `can/haltech_v2_can.xml` | Older/smaller variant, kept for reference. |
| `dashboards/` | Exported RealDash `.rd` dashboard files go here. |
| `docs/hardware.md` | ECU CAN wiring, DTM-4 pinout, termination, adapter choice, head unit USB notes. |
| `docs/realdash-setup.md` | Step-by-step RealDash connection settings that are known to work with Haltech. |
| `docs/can-protocol.md` | Frame-by-frame summary of what the ECU broadcasts and which RealDash input it maps to. |
| `docs/troubleshooting.md` | Symptoms and fixes collected from the RealDash forum and Haltech docs. |
| `docs/reference/` | Haltech CAN Broadcast Protocol V2.35.0 PDF (Haltech's document, kept for reference). |
| `tools/haltech_sim.py` | Bench simulator. Serves fake Haltech CAN frames over TCP in RealDash CAN format so the dashboard can be designed on the head unit with no car attached. |
| `tools/canplayback.py` | RealDash's own tool to replay a CAN log captured in RealDash's CAN Monitor. |

## Quick start

1. Read `docs/hardware.md` and wire the adapter to the ECU CAN bus (DTM-4 or the 26-pin header, one place only).
2. In Haltech NSP: **Haltech CAN System -> Bus Selection = Both Main and Aux**. Without this the ECU is silent on the connector you wired. Set the broadcast protocol to Haltech V2.
3. On the ATOTO, install RealDash from the Play Store, plug the adapter into the USB host port through an OTG adapter, and follow `docs/realdash-setup.md`.
4. To design the dashboard before the car is wired, run `python3 tools/haltech_sim.py` on a laptop on the same Wi-Fi as the head unit and point a RealDash CAN TCP connection at it.
5. Export finished dashboards into `dashboards/` and commit them.

## Status

- [x] Project scaffold, CAN description, docs, bench simulator
- [ ] Adapter purchased and tested on the head unit (see `docs/hardware.md` for the shortlist)
- [ ] ECU wired and NSP CAN settings confirmed
- [ ] First dashboard exported to `dashboards/`
