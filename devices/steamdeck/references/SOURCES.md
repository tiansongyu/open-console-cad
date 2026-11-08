# Steam Deck LCD: source basis

- [Official product specification](https://cdn.cloudflare.steamstatic.com/steamdeck/images/press/techspecs/steamdeck_techspecs.pdf)
- [Firsthand teardown / repair reference](https://www.ifixit.com/News/57101/steam-deck-teardown)

User-selected original model: 2022 LCD. Reference review 2026-09-09. Published complete handheld envelope: 298 × 117 × 49 mm, including controls. The 37 mm front-shell construction datum is an approximate modeling parameter, not the published thickness.

Local contours, internal modules and accessory dimensions are approximate. Photographs are used locally and not redistributed.

Additional original LCD repair references: [motherboard](https://www.ifixit.com/Guide/Steam+Deck+Motherboard+Replacement/148928), [right trackpad](https://www.ifixit.com/Guide/Steam+Deck+Right+Touchpad+Replacement/148981), [right trigger](https://www.ifixit.com/Guide/Steam+Deck+Right+Trigger+Replacement/148900). The motherboard guide includes later revisions; only original silver-shield photographs were used.

## 2026-11-08 Valve exterior-reference review

Valve's [2022 CAD announcement](https://steamcommunity.com/games/1675180/announcements/detail/3106923225208810471) points to the [official hardware repository](https://gitlab.steamos.cloud/SteamDeck/hardware). That endpoint returned an anti-bot denial during this review, so the published files were inspected through the [public mirror pinned to df60b63](https://github.com/KagamiChan/steam-hardware/tree/df60b63ca35b4f922b835ec45252f3b5be535c34). File hashes and exact URLs are recorded in [fidelity_iteration17.json](fidelity_iteration17.json).

The Rev B drawing dated 2022-02-02 specifies active display 151.7 × 95.2 mm and cover glass 173.7 × 106.7 mm on sheet 2. Sparse reference-CAD measurements establish the microphone positions and diameter, touchpad and lower system-key positions, ten speaker openings per side and eleven centered exhaust slots. Drawing keepout annotations are recorded separately from physical aperture dimensions.

The original Valve reference materials use CC BY-NC-SA 4.0 and remain outside the tracked repository. This iteration reconstructs primitives from dimensional facts and counts; it does not embed or redistribute Valve BReps, meshes or drawings. The local curve profiles, sensor-window diameter, support structures and earlier thermal/electronic layout remain estimates, with no factory tolerance or airflow claim.
