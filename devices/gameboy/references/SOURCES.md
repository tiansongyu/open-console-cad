# Nintendo Game Boy DMG-01 — sources

- [Nintendo technical data](https://www.nintendo.com/de-de/Support/Fruhere-Konsolen/Technische-Daten-619585.html): classic model 148 × 90 × 32 mm, 47 × 43 mm LCD, four AA cells, contrast and volume wheels, headphone and link connectors. Reviewed 2026-09-09.
- [iFixit original Game Boy teardown, guide 122657](https://www.ifixit.com/Teardown/Nintendo+Game+Boy+Teardown/122657): DMG-01 front/rear case, six external tri-point fasteners, display board, separate main/power/headphone boards, LCD and speaker attachment, board interconnect. Board parts are a reference revision, not a claim that all DMG-01 boards are identical.

Use the original grey 1989 exterior. Do not substitute Pocket, Color, backlit IPS modifications or rechargeable battery conversions. Local contours, fastener locations, chip packages, contact layouts and wall thicknesses remain approximate CAD-study geometry. Research photographs remain local and are not redistributed. Fonts retain their included license.

## 2026-11-08 · Iteration 16 exterior review

The front, rear, left, right, top and bottom were compared with first-hand photographs, using Nintendo's nominal body envelope as a scale reference. [Brooke Byers' original specimen](https://b13rg.icecdn.tech/Gameboy_DMG/) shows the separated DC/contrast positions, thicker volume wheel, keyed large link socket, removable connector cover, molded arrows and six grille grooves with five openings. Its photographs are used for exterior evidence; unrelated serial-protocol prose is not adopted.

[Pan Docs](https://github.com/gbdev/pandocs/blob/master/src/External_Connectors.md) documents the two-by-three link contact arrangement. [Gekkio's DMG-CPU-06 schematic](https://github.com/Gekkio/gb-schematics/blob/main/DMG-CPU-06/schematic/DMG-CPU-06.pdf), by Joonas Javanainen under CC BY 4.0, records the original 3.5 × 1.35 mm power plug. The model's 3.6 mm socket bore includes an estimated 0.1 mm diametral clearance; it is not a measured socket specification.

[iFixit's Gamebit tool description](https://www.ifixit.com/products/gamebit-3-8mm) identifies the cartridge fastener family as a 3.6 mm line head, commonly called 3.8 mm Gamebit. The local scallop geometry remains fitted.

Nintendo directly publishes 47 × 43 mm screen size. This is retained as a nominal screen window; it does not establish the LCD pixel active area. The Sharp LH1511/LH1512 document found during research describes driver ICs, not the installed LCD module, so it was not used to change the screen geometry.

See [the evidence and uncertainty record](fidelity_iteration16.json) for source-specific claims and photograph hashes. Lettering, port coordinates, groove depths, local curvature and fit clearances are fitted; no complete factory-equivalence or regional-label claim is made. Reference photographs are not redistributed.
