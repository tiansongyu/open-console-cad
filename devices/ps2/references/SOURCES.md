# PlayStation 2 SCPH-10000 — sources

- [Sony SCPH-10000 official manual](https://www.playstation.com/content/dam/global_pdc/en/corporate/support/manuals/ps2-docs/JA_SCPH-10000_WEB.pdf): approximately 301 × 78 × 182 mm (width/height/depth), original front controller/card interfaces, USB and i.LINK S400, rear PC CARD Type III and protector. The included kit identifies a DualShock 2, 8 MB card, AC/AV connections and utility disc. Reviewed 2026-09-10.
- [Dig and Rescue firsthand SCPH-10000 assembly](https://digandrescue.com/hardware/sony/sony-playstation2-scph-10000/): GH-001 family, middle frame and heatsink, separate power supply, optical assembly, ten outer case fixings, four rubber pads and PC CARD protector. Photos 001–005, 007, 009, 013, 016–018, 020–022, 024 and 025 reviewed. The metal heat-spreader plate and curved heat pipes are recorded for the next internal stages.
- [Sony SCPH-10010 DualShock 2 manual](https://www.playstation.com/content/dam/global_pdc/en/corporate/support/manuals/ps2-docs/JA_SCPH-10010_WEB.pdf): original controller family and controls; detailed model-specific internal reference review remains pending.
- [Sony SCPH-10020 memory-card manual](https://www.playstation.com/content/dam/global_pdc/en/corporate/support/manuals/ps2-docs/JA_SCPH-10020_WEB.pdf): original 8 MB memory-card identity; detailed construction remains pending.

The study selects the Japanese SCPH-10000 with PC CARD, not a later EXPANSION BAY case. X runs across the front, Y towards the rear and Z upwards. The stepped lower-body split, wall thickness, ribs, markings and later component locations are photographic study estimates. The official overall body dimensions do not establish production wall or hole tolerances.

Research photographs and downloaded manuals remain in the ignored local workspace and are not redistributed. The geometric top mark is a study approximation. DejaVu Sans follows the root third-party font notice. This work is a nonfunctional structural study, with no game data or electrical netlist.

The original manual page 15 places PC CARD on the lower rear, separate from the AV MULTI and optical outputs; the upper rear contains the mains rocker, figure-eight inlet and fan opening. Front connector drawings preserve two rows of card/controller access, the original blue USB/i.LINK field, and the narrow power/eject board. Functional labels use readable study text; local connector, spring and solder-tail geometry remains approximate.

[Stout256, four-pin FireWire socket diagram](https://commons.wikimedia.org/wiki/File:Image-FireWire_4_Pin_Connector_Pinout.svg) (CC0): visual cross-check of the four inline contacts beneath the tongue. Used as connector-family reference, not a claim to identify the original component manufacturer.

## Mainboard and lower shielding

- [Rodrigo Copetti, PlayStation 2 architecture](https://www.copetti.org/writings/consoles/playstation-2/): the author photographed his own SCPH-10000 GH-001 board. The original and annotated images guide the EE/GS, two RDRAM devices, IOP, RAM, audio, regulator and RTC regions. His lower-right ROM identification is explicitly a presumption, so this study labels it `ROM STUDY`. Reviewed 2026-09-10.
- [PS2 developer hardware research, Graphics Synthesizer](https://www.psdevwiki.com/ps2/Graphics_Synthesizer): cross-check of the early CXD2934GB metal-lid family and 384-ball package. The modeled ball grid is schematic, with no manufacturer pin assignment.
- [CPU Collection, Sony Emotion Engine](https://www.cpu-collection.de/?l0=co&l1=Sony&l2=Emotion+Engine&tn=0): an owned later-family specimen supports a 540-ball package-family reference only. It does not establish the launch chip revision; the CXD9542GB study legend is taken from the GH-001 board photograph.
- Dig and Rescue photos 004, 006, 014 and 015 additionally guide the opposite board face, three-position fan connection, flat-circuit connections, lower shield contact fingers and four shield fixings. Unreadable underside IC identities remain descriptive labels, not asserted part numbers.

The 248 × 157 mm board outline, component positions, mounting pattern, all small package outlines and leads, passive-component selection, wiring clearances, shield thickness and bends are local study approximations. Native connector passages are modeled individually. The BGA patterns and visible package leads describe assembly structure only; they do not reconstruct a PCB netlist, production BOM or repair-ready board. Reference imagery is not bundled with the MIT model assets.

## Frame, cooling and internal power board

Dig and Rescue photos 001, 002, 005, 007, 008, 011 and 015 were visually reviewed for the middle frame, folded heat-spreader assembly, curved heat pipes, fin bank, rear axial fan, transformer, twin primary capacitors, filter chokes and original power-board corner coupling. Reviewed 2026-09-15. The study preserves these separate assemblies. Nine mainboard fixings and the pair of washer-equipped heat-sink fixings follow the documented assembly sequence.

The internal frame dimensions, support ribs, screw lengths, seven-blade rotor shape, fin count and thickness, heat-pipe paths, power-board dimensions, coupling length and small electrical-package selection are local reconstruction choices, not manufacturer measurements. Electrical markings are descriptive and the PSU has no electrical netlist. No claim is made for thermal performance, mains safety or repair interchangeability. All locally modeled clearances are checked as CAD assembly relationships.

## Original optical mechanism

- [Secret Base Manager, firsthand SCPH-10000 teardown](https://secretbase-manager.hatenablog.com/entry/2020/03/20/142040): opened-drive and removed-tray photographs guide the long tray access opening, longitudinal rack, guide rods, spindle location, pickup carriage, isolation mounts and original cover. Selected full-size photographs were inspected locally and are not redistributed.
- [PS2 Developer Wiki, CDVD Drive](https://www.psdevwiki.com/ps2/CDVD_Drive): the early A-chassis family uses the KHS-400A pickup and a separate GM-038 board with Sony CXA2605R RF amplifier and thermal interface. The study retains those early architectural features.

Reviewed 2026-09-15. The exact small-board outline, package leads, optical-block internals, gearing, belt profile, rack pitch, motor dimensions and fastening geometry are schematic reconstruction choices. The assembly shows a closed tray; it does not simulate focus, tray motion, electrical behavior or laser operation. Later KHS-400C mechanisms and later all-on-mainboard drive electronics are not used as substitutes for the selected version.

## Wiring and case attachment

Dig and Rescue and Secret Base Manager assembly photographs guide the fan lead, shared controller/card-board ribbon, optical connection, control-button harness and its ferrite/guide posts. Ten underside case fixings, two longer rear-side fixings, four rubber feet and six removable screw covers are represented. Local cable paths, pin selections, conductor spacing, fixing dimensions and snap geometry are study approximations. The wiring shows physical routing and component relationships; it is not a service wiring diagram or electrical netlist. The lower model label explicitly identifies this as a CAD study.
