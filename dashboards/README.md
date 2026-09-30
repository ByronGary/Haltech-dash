# Dashboards

Export dashboards from RealDash (Garage -> dashboard -> Export) and drop the `.rd` files here.

Naming: `haltech_<purpose>_v<N>.rd`, for example `haltech_street_v1.rd`.

Any dashboard that uses a custom `name="Haltech: ..."` input only works when the same
`can/haltech_v3_can.xml` is loaded on the head unit. Prefer stock RealDash inputs where a
`targetId` exists so the dash keeps working if the XML changes.
