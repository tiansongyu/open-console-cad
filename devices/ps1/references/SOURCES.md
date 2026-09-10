# PlayStation SCPH-1000 — sources

- [iFixit firsthand teardown, guide 128089](https://www.ifixit.com/Teardown/Sony+PlayStation+Teardown/128089): Japanese SCPH-1000, original grey enclosure, rear S-Video, RCA, RFU DC, serial and parallel interfaces; separate front-port assembly, rubber-mounted optical drive, power board and PU-7 electronics. The controller in this study will be the original digital type, without analogue sticks. Reviewed 2026-09-09.
- [Sony SCPH-5500 user manual](https://www.playstation.com/content/dam/global_pdc/en/corporate/support/manuals/ps-docs/JA_SCPH-5500_WEB.pdf): later original-family width 270 mm, height 60 mm and depth 188 mm, used only as an approximate dimensional reference. This manual does not establish the SCPH-1000 board layout or its additional rear ports.
- [PSX-SPX reverse-engineering pinout research](https://psx-spx.consoledev.net/pinouts/): controller/card connectors, eight-pin serial, single-row twelve-pin AV Multi Out and two-row 68-pin parallel connector. Contact geometry is schematic and does not implement an electrical netlist.
- [Dig and Rescue firsthand SCPH-1000 assembly](https://digandrescue.com/hardware/sony/sony-playstation-scph-1000/): lower shield, main shield with six fixings, separate front-interface cover with five fixings, power-board retaining points, lid mechanism, rectangular feet and six outer case fixings. Photographs guide the mechanical layout; local coordinates remain approximate.

CAD coordinates use X across the front, Y towards the rear and Z upwards. All SCPH-1000 study dimensions remain approximate until a model-specific dimensional drawing or physical measurement is verified. Shell walls, moulding, fasteners, connectors and electronic packages are study geometry. The separate memory-card capacity is 1 Mbit (128 KiB), not 1 MB. No game image, firmware or electrical netlist is included.

Research photographs and downloaded manuals remain in the ignored local workspace and are not redistributed. DejaVu Sans retains its original font license in the root third-party notices.

Rear functional labels in the study use English for readability; the photographed Japanese console has Japanese legends. All dedicated SCPH-1000 rear connector positions are retained.

The mainboard reference is the photographed PU-7 `1-655-322-13A`, not a claim to reproduce the earliest production batch. Package counts and layouts are cross-checked with PSX-SPX. CXD2923AR is the video RGB converter; the separate AK4309VM handles audio conversion. Pad outlines and conductor locations remain geometric studies.

The separate supply follows the firsthand `1-413-997-13` board photograph, including its seven-position connector, rectangular input-choke core, transformer and glass fuse. Internal winding packs, device package placement, wire lengths and colours are approximate. No mains or low-voltage electrical netlist is provided; the geometry is not a working supply design.

- [Dig and Rescue SCPH-1010 controller assembly](https://digandrescue.com/hardware/sony/sony-playstation-scph-1010-controller/): original digital controller, separate shoulder assemblies, membrane contacts, phenolic board and eight rear case fixings. This model follows the compact Japanese controller, not the larger SCPH-1080 or a DualShock. Outline control points and dimensions are photographic approximations.

- [Dig and Rescue SCPH-1020 memory card](https://digandrescue.com/hardware/sony/sony-playstation-scph-1020-memorycard/): firsthand photographs show two board sizes under the same model number, a sliding rear cover, two screws, eight edge fingers and the original grey face. The larger board is used for this study; the source author only tentatively dates the smaller version later, so this is not a verified launch-board attribution. The 42 × 57 × 7.6 mm card envelope, package bodies, pin counts and passives are local geometric approximations. Reviewed 2026-09-10.

The detached connection set uses a Japanese two-blade mains plug, figure-eight device connector and twelve-position single-row AV MULTI to three RCA plugs. Contact identities follow the PSX-SPX reference; the modeled cable lengths and internal conductors are display studies. The blank CD contains no game data.
