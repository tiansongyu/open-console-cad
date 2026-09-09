# PlayStation SCPH-1000 — sources

- [iFixit firsthand teardown, guide 128089](https://www.ifixit.com/Teardown/Sony+PlayStation+Teardown/128089): Japanese SCPH-1000, original grey enclosure, rear S-Video, RCA, RFU DC, serial and parallel interfaces; separate front-port assembly, rubber-mounted optical drive, power board and PU-7 electronics. The controller in this study will be the original digital type, without analogue sticks. Reviewed 2026-09-09.
- [Sony SCPH-5500 user manual](https://www.playstation.com/content/dam/global_pdc/en/corporate/support/manuals/ps-docs/JA_SCPH-5500_WEB.pdf): later original-family width 270 mm, height 60 mm and depth 188 mm, used only as an approximate dimensional reference. This manual does not establish the SCPH-1000 board layout or its additional rear ports.
- [PSX-SPX reverse-engineering pinout research](https://psx-spx.consoledev.net/pinouts/): controller/card connectors, eight-pin serial, single-row twelve-pin AV Multi Out and two-row 68-pin parallel connector. Contact geometry is schematic and does not implement an electrical netlist.

CAD coordinates use X across the front, Y towards the rear and Z upwards. All SCPH-1000 study dimensions remain approximate until a model-specific dimensional drawing or physical measurement is verified. Shell walls, moulding, fasteners, connectors and electronic packages are study geometry. The separate memory-card capacity is 1 Mbit (128 KiB), not 1 MB. No game image, firmware or electrical netlist is included.

Research photographs and downloaded manuals remain in the ignored local workspace and are not redistributed. DejaVu Sans retains its original font license in the root third-party notices.

Rear functional labels in the study use English for readability; the photographed Japanese console has Japanese legends. All dedicated SCPH-1000 rear connector positions are retained.

The mainboard reference is the photographed PU-7 `1-655-322-13A`, not a claim to reproduce the earliest production batch. Package counts and layouts are cross-checked with PSX-SPX. CXD2923AR is the video RGB converter; the separate AK4309VM handles audio conversion. Pad outlines and conductor locations remain geometric studies.
