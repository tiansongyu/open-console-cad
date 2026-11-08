# Sega Mega Drive references

- [Official hardware information](https://www.sega.jp/history/hard/megadrive/index.html).

Native geometry, local dimensions and internal layout are original study approximations. Reference photographs are used for research only and are not redistributed. DejaVu Sans is used under its existing repository license.

- [HAA-2510 VA2 firsthand teardown](https://digandrescue.com/hardware/sega/sega-megadrive-haa2510-va2/): cartridge flap and power interlock, 64-contact reader, board components, regulator heat spreader, ten board/chassis fixings and six case screws. The exterior is the original Model 1 family; the internal study uses VA2 photographs, not a claim to reproduce the earliest VA0 circuit.
- [SJ-3500 three-button control pad](https://digandrescue.com/hardware/sega/sega-megadrive-sj-3500-controlpad/): curved casing, separate ABC/START rubbers, phenolic PCB and six rear screws.
- Official SEGA dimensions: 280 W × 212 D × 70 H mm. Local dimensions, connectors, lettering and internals are approximate; connector protrusions are measured separately.

## 2026-11-08 AV connector correction

[Same Sky's SD series drawing](https://www.sameskydevices.com/product/resource/sd.pdf), dated 2024-09-12, specifies the SD-81 DIN-8 262° interface on page 3. [Retro Access](https://retro-access.com/product/connector-din8-262/) identifies that connector type as compatible with Mega Drive Model 1. The model's eight equally spaced contacts are replaced by seven outer contacts and one contact 0.9 mm above the centre, with matching socket holes and a top polarising key. Male pins are 1.5 mm in diameter and the mating barrel is 13.2 mm, following the drawing.

This is a compatible interface reference, not proof of the original SEGA connector supplier. The 4.25 mm contact-circle radius is scaled from the drawing; socket clearances, axial dimensions, board placement and cable hood remain approximate. Exact changes and source hash are in [fidelity_din8_262.json](fidelity_din8_262.json).
