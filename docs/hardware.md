# Hardware

## Parts

| Role | Part | Notes |
|------|------|-------|
| ECU | Haltech Elite 2500 | CAN available on the main 26-pin connector **and** on the dedicated DTM-4 CAN connector. Use one, not both. |
| Adapter | USB CAN adapter, see shortlist below | Must be on RealDash's supported list; a generic SocketCAN or ELM327 dongle will not work for a raw 1 Mbit Haltech bus. |
| Head unit | ATOTO S8 Gen2 Standard | Android, USB host via OTG. Only one "storage" USB port on the Standard tier; the "Phone Link" port does not accept serial adapters. |
| Cabling | Haltech DTM-4 CAN cable or a DTM-4 plug + twisted pair | 120 ohm termination needed at each end of the bus. |

## Adapter shortlist (from RealDash's supported list)

| Adapter | Connection | Android | RealDash serial baud | Comment |
|---------|------------|---------|----------------------|---------|
| Waveshare USB-CAN-A | USB serial | Yes | 1228800 recommended (2000000 default) | Cheap, widely used with Haltech on RealDash. Configure with Waveshare's Windows tool first. |
| Seeed Studio USB-CAN Analyzer (RealDash "CAN Analyzer Type 1") | USB serial | Yes | 1228800 recommended (2000000 default) | Same family as the Waveshare. The nextez Haltech RealDash project uses this one. |
| CANable (SLCAN firmware) | USB serial | Yes | 2000000 for CANable 2.0 | Generic SLCAN support. |
| Robotell USB-CAN | USB serial | Yes | 115200 default | Needs power cycle after config changes. |
| CAN Analyzer Type 2 (LDXN) | USB serial | Yes | Automatic | |
| MeatPi CAN adapter | Wi-Fi or Bluetooth | Yes | Automatic | Avoids the USB port entirely. Fallback if the ATOTO's USB host is trouble. |

Recommendation: **Waveshare USB-CAN-A** first. It is the cheapest, it is on the supported list, and there are
multiple RealDash forum reports of it working with Haltech. Keep the MeatPi (Wi-Fi) in mind as the fallback if
the ATOTO's USB host port refuses to hand the device to RealDash.

Full list: https://realdash.net/manuals/supported_can_lin_analyzers.php

## ECU CAN wiring

DTM-4 CAN connector pinout (Haltech Elite):

| Pin | Signal | Haltech cable colour |
|-----|--------|----------------------|
| 1 | +12 V switched | Red |
| 2 | Ground | Black |
| 3 | CAN High | White |
| 4 | CAN Low | Blue |

- Twisted pair for CAN H / CAN L. Keep the stub to the adapter short.
- Two 120 ohm terminators, one at each physical end of the bus. The Elite has one internally at the ECU end
  in most configurations; check the Haltech CAN wiring guide for the Elite 2500 and add the second at the
  adapter end if the adapter does not have one switchable. Measure ~60 ohm between CAN H and CAN L with
  everything powered off when termination is right.
- If you already have Haltech CAN devices (wideband, keypad, IO box) on a CAN hub, the adapter just becomes
  another node on the hub. Do not add a third terminator.
- Do not power the adapter from the DTM-4 12 V pin unless the adapter is designed for it. The USB side is
  powered by the head unit.

Haltech guide: https://support.haltech.com/portal/en/kb/articles/elite-1500-2500-can-communications-wiring-guide

## ECU software (NSP) settings

1. **Haltech CAN System -> Bus Selection = Both Main and Aux Connectors.** This is the number one cause of
   "adapter connects but no data" on the RealDash forum.
2. **Vehicle CAN System** (if used): choose which connector it lives on so it does not collide.
3. CAN broadcast protocol: **Haltech V2** (the default on Elite). Speed is fixed at 1 Mbit/s.

## Head unit notes (ATOTO S8 Gen2 Standard, S8G2A74SD)

| Spec | Value |
|------|-------|
| SoC | UNISOC 7862, 8x Cortex-A55 up to 1.8 GHz, Mali-G52 MP2, 12 nm |
| RAM / storage | 3 GB / 32 GB |
| OS | ATOTO AICE UI 11 on Android 10 |
| Screen | 7 in, 1024x600 IPS, 600 nits |

### Is it fast enough?

Yes for this job. RealDash is a native OpenGL app that runs on 2 GB tablets; 3 GB is fine and the head unit
is not multitasking anything heavy while the dash is up. The bottlenecks, in order, are:

1. **USB serial throughput, not RAM or GPU.** The adapter turns every CAN frame into ~20 serial bytes. The
   full Haltech V2 broadcast is roughly 600 frames/s (about 2000 values/s), which at 1228800 baud uses
   ~10% of the link. Busy buses (extra Haltech CAN devices, a second ECU protocol enabled) push the adapter
   into buffering and you get the 1-2 s "rubber band" lag reported on the RealDash forum. Mitigation is on
   the ECU side: in NSP turn off broadcast groups you do not display, keep only one broadcast protocol on.
2. **Gauge rendering cost.** The Mali-G52 MP2 is a budget GPU. Avoid full-screen blur, glow, drop shadows
   and large animated backgrounds. Plain needles, bars and text run at 60 fps; effects-heavy dashboards
   from the RealDash store can drop to 20-30 fps on this class of SoC.
3. **The AICE launcher.** ATOTO's skin keeps its own services resident. Disable ATOTO's boot animation and
   any radio/EQ widgets you do not use, and set RealDash as the auto-start app.

Not a concern: Android 10 predates the API 34 USB permission bug, and the 1024x600 panel is a light pixel
load.

### CarPlay / Android Auto alongside RealDash

- RealDash cannot run *inside* CarPlay or Android Auto. Both projection APIs only admit media, messaging
  and navigation app types; the RealDash developer has said its game-engine renderer will never be allowed.
  So on the ATOTO they are two separate full-screen apps and you switch between them.
- No USB port conflict. The CAN adapter lives on the storage port; the phone uses wireless CarPlay/AA on
  this model, or the dedicated phone-link port if wired. Never put the CAN adapter on the phone-link port.
- Wireless CarPlay/AA uses the head unit's Wi-Fi as a peer-to-peer link. That is one more reason to use a
  USB CAN adapter rather than a Wi-Fi one (MeatPi), and it means the bench simulator over Wi-Fi may fight
  with wireless CarPlay. Bench test with CarPlay disconnected.
- When CarPlay is in front, RealDash is in the background. It keeps the USB connection and keeps logging as
  long as Android does not kill it; exclude RealDash from battery optimisation and keep the dashboard light
  so memory pressure stays low. You will not see RealDash warnings while CarPlay is in front; there is no
  overlay mode.
- ATOTO's split screen is for its own apps. CarPlay/AA projection will not share the screen with RealDash.
- Practical layout: RealDash as the auto-start home screen with a big button that launches the CarPlay app,
  and the head unit's hardware "home" key mapped back to RealDash. Navigation and gauges at the same time
  needs a second display or the phone on a mount.

- Use a proper USB OTG adapter on the storage port. Some cheap OTG cables do not wire the ID pin and the
  head unit never enters host mode.
- Android will prompt for USB permission for RealDash the first time; tick "always allow". RealDash fixed an
  Android API 34+ permission regression in 2024, so keep RealDash updated from the Play Store.
- Set the head unit to not sleep USB on screen-off, and set RealDash to auto-start with the connection
  enabled, so the dash comes up with ignition.
- Screen resolution on the Standard is 1024x600. Design the dashboard at that aspect.
