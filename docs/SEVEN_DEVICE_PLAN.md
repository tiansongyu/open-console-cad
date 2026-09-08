# Seven-device expansion

User-confirmed models (2026-09-08): Nintendo 3DS CTR-001, Nintendo DS NTR-001, PSP-1000, PS Vita PCH-1000 OLED, Steam Deck LCD (2022). Switch HAC-001 and Switch 2 BEE-001 remain in the collection.

## Acceptance scope

Each new device receives an independent `devices/<id>/` project with native editable CAD, distinctive exterior details, schematic major internals, meaningful staged source history, assembled and exploded files, colored STEP, component inventory, dimensioned A3 drawings, and generated previews. Hinged devices also receive open/closed pose handling. Local features and internal dimensions are approximate, with published envelopes and sources explicitly identified.

Modeling continues through neka-nat/freecad-mcp. Validate physical shapes, interfaces/interference, relevant parameter or pose changes, native reload, source rebuild, STEP round trips and drawing dimensions. New PDFs use the installed Kami workflow and per-page/font verification. Commit reviewable modeling milestones and verified device deliveries.

The final Pages catalog must contain seven working device entries with directly linked README previews, actual GLB component geometry, mode selection and exploded views. Do not publish placeholder entries or mark a device complete before its files and views are verified.

## Baseline verification

Switch and Switch 2: latest Pages workflow successful at commit f05787f. Both live GLB files fetched from Pages and compared with local SHA-256 on 2026-09-08; both matched.

## Planned model stages

1. Parameterized housing and enclosure cavities.
2. Display layers and device-specific main structure.
3. Primary controls and legends.
4. Connectors, slots and side controls.
5. Speakers, cameras, sensors and ventilation.
6. Rear details, service access and relevant accessories.
7. Battery and mounting structure.
8. Main board, daughterboards and major packages.
9. Control mechanisms and flex interconnects.
10. Fasteners, shielding and structural details.
11. Measured assembly clearances and fit corrections.
12. Pose/service refinements and final presentation geometry.

Additional corrective stages are recorded when inspection finds defects; the list is a build sequence, not a substitute for completion checks.

| Device | State |
| --- | --- |
| Switch | Existing published baseline verified |
| Switch 2 | Existing published baseline verified |
| Nintendo 3DS | 13 stages / 324 components; native, STEP, 12-page drawings and hinge-capable web preview verified; release ready |
| Nintendo DS | 15 stages / 321 components; native, STEP, 12-page drawings and live hinged web preview verified at 3ec3907 |
| PSP-1000 | 14 stages / 346 components; native, STEP, twelve A3 sheets and detailed web preview verified; release ready |
| PS Vita PCH-1000 | Reference preparation |
| Steam Deck LCD | Reference preparation |
