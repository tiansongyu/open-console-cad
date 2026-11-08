# Nintendo Wii reference basis

Selected exterior: original white **RVL-001**, with four GameCube controller ports and two GameCube memory-card slots. The model uses the supported horizontal orientation: X = 157 mm, Y = 215.4 mm, Z = 44 mm. Original RVL-003 Remote and RVL-004 Nunchuk are the controller targets.

| Source | Scope used |
| --- | --- |
| [Nintendo: Wii console](https://www.nintendo.co.jp/wii/console/index.html) | Official body dimensions excluding protrusions; original GameCube compatibility and connector inventory. Its later bundled Remote Plus listing does not define this model's controller variant. |
| [Nintendo: Wii setup manual, printed pp. 26–27](https://www.nintendo.co.jp/wii/support/pdf/wiimanual_setup.pdf) | Front, rear, GameCube compartment and underside connector arrangement; supported horizontal placement. |
| [Nintendo: original RVL-003 Remote manual](https://www.nintendo.co.jp/support/manual/wiiu/accessories/pdf/RVL-A-C-JPN.pdf) | Original Remote model identification, controls and dimensions. The Remote Plus is excluded. |
| [Dig and Rescue: RVL-001 teardown/reassembly](https://digandrescue.com/hardware/nintendo/nintendo-wii-rvl-001/) | Direct photographs of faceplate illumination, GameCube sockets, heatsink, shields and slot-loading drive. |
| [iFixit: Wii motherboard replacement](https://www.ifixit.com/Guide/Nintendo+Wii+Motherboard+Replacement/3460) | Direct board, fan, heatsink and removable radio photographs. The photographed RVL-CPU-40 board is a layout reference, not a claim of first-production PCB fidelity. |
| [iFixit: Wii teardown](https://www.ifixit.com/Teardown/Nintendo+Wii+Teardown/812) | Direct 2009 teardown observations of the original enclosure, layered assembly and disc mechanism. |

- [Nintendo sensor-bar functionality check](https://en-americas-support.nintendo.com/app/answers/detail/a_id/2954/p/604/c/947): the original reference uses five infrared emitters at each end.

Sources checked on 2026-09-10. Reference photographs and manuals are kept in the local research cache and are not redistributed.

The body envelope follows the official dimensions. Wall thickness, connector positions and contact shapes, chips, interconnect fields, passive-component banks and mechanisms are original study approximations. They do not reproduce a production PCB netlist, manufacturing tolerances, electrical behavior or tested motion. Internal component counts describe this CAD model only.

DejaVu Sans is used for CAD markings under its existing repository license. Final document typography follows the shared Kami workflow.

## 2026-11-08 exterior comparison

The original RVL-001 setup diagrams (printed pages 26–27) were compared with front, rear and open-GameCube-side CAD views. This corrects the cover proportion, wordmark orientation, narrow front controls, rear five-by-five grille and close USB pairing. Port size/pitch and RGB values are image fits, not factory dimensions.

The [original Remote product photograph](https://www.nintendo.co.jp/wii/controllers/img_wiiRemote/phShiro.jpg) was normalized to the published 36.2 × 148 mm frontal envelope. The existing controls were too low; the key stacks, apertures, contacts, speaker and lamps now follow that fit. The original manual corroborates the eighteen-hole grille, one-to-four player dots, rear SYNC control and lanyard attachment. Pixel bounds and target coordinates are in [fidelity_iteration16.json](fidelity_iteration16.json).

The manufacturer [2006 strap notice](https://www.nintendo.co.jp/wii/news/strap.html) distinguishes early and replacement cords. The later manual's RVL-018A strap and jacket are not added; this pass changes the original Remote housing only. Reference imagery remains local. Detailed shell profiles, hardware tolerances and the PCB arrangement remain unverified.
