# Art direction and asset provenance

## Openly licensed source packs

### Current city: original Cytopia artwork

The current city uses **31 original PNG sheets** copied directly from [Cytopia](https://github.com/CytopiaTeam/Cytopia), at revision `c70bbce3ba8b0ba23b8dcce9ff8bc8df0af971f8`, under the upstream repository's **GNU GPL version 3**. The original sheets are unchanged and included as the editable source. Author names, upstream paths, dimensions and SHA-256 hashes are recorded in `kiraku/static/assets/cytopia/manifest.json`; tests verify every original file against that hash.

The imported set includes small houses, apartments, shops, civic office towers, public parks, ground tiles, roads, trees and street lights. The individual artists are credited in the manifest and the complete upstream `UPSTREAM-CREDITS.txt`. The GPL text is included as `LICENSE-GPL-3.0.txt`. Extracted first-frame previews retain the source artwork's licence and are identified as derived files in `NOTICE.txt`.

Phaser selects native frames and uses nearest-neighbour scaling. The renderer adds Kiraku's mission signs, dashed lot outlines, issue flags and construction effects. The world is 40 × 40 tiles, with four navigable districts, 102 saved starting buildings and 16 open mission plots. No Cytopia C++ engine code has been imported. The new camera supports panning, scroll zoom, district travel, overview and a state-based minimap.

The town's four visual families are vegetation green; warm brick, red and amber; cream and grey masonry/infrastructure; and the blue windows present in the original city art. The HTML palette remains exactly as specified in the brief. Building shapes and readable Malay names identify the case types while preserving the imported artwork.

### Earlier prototype assets retained in the project

- **Kenney — Isometric Tiles City / Isometric City**, 128 2D sprites, **CC0 1.0 Universal**. [Artist's pack page](https://kenney.nl/assets/isometric-tiles-city), [artist's OpenGameArt upload](https://opengameart.org/content/isometric-city). Downloaded from the artist's alternate upload because the first Kenney download URL returned an HTML page.
- **Kenney — Isometric Tiles Buildings / Isometric Buildings #1**, modular 2D building sprites, **CC0 1.0 Universal**. [Artist's OpenGameArt upload](https://opengameart.org/content/isometric-buildings-1).

The older Kenney pack licenses are in `kiraku/static/assets/licenses/`. `pixel/SOURCES.json` records each earlier source sprite and its SHA-256 hash. Those low-resolution prototype building adaptations are retained for provenance and are no longer the city models. The original Pelita, NPC and car sprites remain in use. The current Cytopia sheets are not recoloured or resampled files.

Original owl, NPCs, two-frame walks, cars, signs and adaptation details are CC0 under `pixel/LICENSE.txt`. The mark in the header is an original geometric city mark. No third-party company logo or image-generation service is used.

## Four colour families

The table below records the original prototype's colour intent. The current imported city follows the Cytopia palette described above; its parks retain recognisable lawns, trees and benches, and its roads retain white dashed lines. Outcome and warning colours remain consistent across both versions.

| Family | Meaning | Shape and details |
| --- | --- | --- |
| Warm red, cream, amber | Shops, lights and opportunities | Gabled red roof, cream walls, flower pots, lit cream sign. Taxi stand has a low amber canopy and square sign. Amber also marks a waiting plot. |
| Greens | Stalls, parks and vegetation | A stall has a broad green awning and market counter. A park has a lawn, multiple trees, a bench and a low base. |
| Grey and dark neutral | Roads and infrastructure | Grey isometric road tiles, white dashed centre lines, zebra crossings and neutral windows. |
| Night blue and cream | Interface and readable labels | Solid night background, solid panels, cream text and dark-outlined map labels. Information blue is reserved for the HTML agent trace. |

The art uses no gradients, glow or blur. Text and controls follow the brief's night-blue `#1B2433`, panel `#26324A`, cream `#F4F1EA`, amber `#FFB23F`, green `#4CC38A`, rejected red `#FF6B5A`, and information blue `#7CC4FF` palette. Font roles: Inter for the interface; Press Start 2P only for town labels and the Demo footer label. Map text stays at least 14 rendered pixels after fitting or zooming. On phones, a limited set of focus labels avoids collisions; the building list supplies all names.

## Maths-to-town mapping

| Case | Verified final condition | Saved town effect |
| --- | --- | --- |
| Kedai Bunga Melur | Reverse successive percentages, then calculate final selling price minus cost. Profit must reach target T. | Open or upgrade the shop; shops +1. |
| Teksi Kiraku | Remove the flag fee to find distance, then include it in the new fare. | Open or upgrade a taxi stand; stands +1. |
| Gerai Taman | Recover the missing daily sale and identify the unique mode. The mode must reach the target. | Open or upgrade a stall; stalls +1. |
| Taman Kiraku | Solve width and length, cost one long fence side, and find shortfall. Shortfall must be zero. | Fund or upgrade the park; parks +1. A correct positive shortfall holds the project. |

An empty plot has a dashed pixel outline, a small sign and a Kosong label; English appears on hover or in details. An open issue adds an amber flag. A rejected step changes the warning state only: it never builds a building or increments a count. The next Quest decision sends an amber pixel from the trace's direction to the assigned plot. A funded result triggers 600 ms growth, a short dust puff and a lit shop sign after returning to town.

Seven NPCs use two-frame walks along the road network. Three cars traverse the outer road loop. A pause control and `prefers-reduced-motion` stop traffic; reduced motion makes construction and pulses immediate. The background has a single flat tint, with no day/night system.

The landing image is a genuine capture of this Phaser canvas. The screenshots in `docs/screenshots/` show the actual UI, saved cases and real construction tween, rather than a design mockup.
