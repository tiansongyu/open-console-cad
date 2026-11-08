# Sega Saturn references

- [Official hardware information](https://www.sega.jp/history/hard/segasaturn/index.html).

Native geometry, local dimensions and internal layout are original study approximations. Reference photographs are used for research only and are not redistributed. DejaVu Sans is used under its existing repository license.

- [HST-3200 firsthand teardown](https://digandrescue.com/hardware/sega/sega-segasaturn-hst-3200/): grey original model with oval controls; PSU is mounted to upper housing. The official SEGA table identifies HST-3210 and lists 260 W × 230 D × 83 H mm. These are a family reference only for this HST-3200 study; original-model dimensions remain approximate.

- [SEGA original peripherals](https://www.sega.jp/history/hard/segasaturn/devices.html): HSS-0101 controller family identification.
- [HSS-0101 firsthand teardown](https://digandrescue.com/hardware/sega/sega_segasaturn_hss-0101_controller/): original grey six-button pad, shoulder controls and internal board.
- [Plutiedev I/O connector work](https://www.plutiedev.com/io-pinout): Saturn controller's single row of nine connections.

Sources checked on 2026-09-10. HST-3200 mainboard photos show a MAIN VA0.5 layout and a separate CD subsystem board. These are study references, not a claim of production netlist or pinout accuracy.

The HSS-0101 teardown includes the later mist-grey colour scheme as well as the original grey pad. The original grey front/rear photographs define this model's exterior; the shared board and silicone construction is used only as a family-level internal reference. The finished model uses black ABC and blue XYZ/START keys. The controller's local dimensions are study estimates.

All harness routes, spring/gear dimensions, adapter contacts and cartridge contact shapes are original CAD study geometry. Blank 12 cm media contains no game data or copyrighted game image. The electronics do not implement a circuit netlist, electrical behaviour or tested motion.

## Iteration 23, checked 2026-11-08

[Anders Montonen’s USB cartridge](https://github.com/andersm/usbcart), commit `8ae97586e01dcc76b1f93e19c9b468263c56eb65`, supplies the original KiCad footprint and board edges: 67 contacts per face, nominal 1.0 mm pitch, 36/31 groups and a 6 mm locating notch. The board declares 0.0001 inch units; values are converted with 0.00254 mm quantization. This establishes compatible card-edge geometry, not an original SEGA connector supplier.

[Volex’s August 2025 catalogue](https://www.volex.com/media/0dodxec5/volex-power-cords-catalogue-august-2025.pdf), pages 228–229, specifies the compatible C7 8.6 mm contact centres and nominal 16.0 × 7.85 mm front profile. [Retro Access’s connector guide](https://retro-access.com/knowledge-center/connectors/) confirms the 9.5 mm mini-DIN male sleeve and Saturn’s off-standard female socket. The original HST-3200 rear photograph provides the T-shaped power plate and key orientation.

File hashes, dimensional derivation and remaining estimates are recorded in [fidelity_iteration23.json](fidelity_iteration23.json). The controller’s matched 2.55 mm study pitch and retained C8 pin diameter are not asserted to be OEM measurements.
