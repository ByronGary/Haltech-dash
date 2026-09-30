# Troubleshooting

Ordered by how often each one turns out to be the cause on the RealDash forum.

## Adapter connects, CAN Monitor shows nothing

1. **NSP: Haltech CAN System -> Bus Selection is not "Both Main and Aux".** The ECU only transmits on the
   connector you selected. Set it to both, save, power cycle the ECU.
2. CAN speed in RealDash not 1000 kbps, or frame type not Standard.
3. Serial baud not matching the adapter. Seeed/Waveshare default to 2000000; RealDash recommends 1228800 and
   the adapter must be set to the same value with its Windows tool. The LED blink pattern on the Seeed
   indicates the current baud.
4. CAN H / CAN L swapped, or no termination. Check for ~60 ohm across H and L with power off.
5. Waveshare only: set **Protocol = variable length** and **only send once** in the Waveshare config tool.

## RealDash does not see the USB device at all

- OTG adapter not switching the port to host mode. Try a different OTG adapter; the one that comes with USB
  sticks usually works.
- Plugged into the ATOTO "Phone Link" port. Use the storage port.
- Android USB permission was denied once. Settings -> Apps -> RealDash -> clear defaults, replug, accept the
  prompt and tick "always".
- Old RealDash build on Android 14+. Update from the Play Store (the USB permission fix landed in 2024).

## Values are wrong by a constant

- Temperatures off by 273: `units="K"` missing on that value in the XML.
- Pressures reading ~101 too high: it is absolute; add `- 101.3` to the conversion.
- Trims wrong when negative: `signed="true"` missing.
- Everything scrambled: the frame is missing `endianess="big"` (Haltech is big-endian).

## Dashboard works on the laptop but not on the head unit

- A gauge bound to a custom `Haltech: ...` input needs the same XML loaded on the head unit.
- 1024x600 screen: dashboards designed at 16:9 will crop. Design at the head unit's resolution.

## Connection drops when the screen sleeps

- ATOTO power settings: keep USB powered on screen-off, disable battery optimisation for RealDash, and use
  RealDash's auto-connect on start.
