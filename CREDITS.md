# Credits and licenses

| Component | Use | License / source |
| --- | --- | --- |
| Python | Application runtime | [PSF License](https://docs.python.org/3/license.html) |
| Flask 3.1.0 | JSON API, templates and static files | [BSD-3-Clause](https://github.com/pallets/flask/blob/3.1.0/LICENSE.txt) |
| SQLite / Python sqlite3 | Saved fictional progress | [SQLite public domain](https://www.sqlite.org/copyright.html); Python wrapper under the PSF license |
| Phaser 3.80.1 | Isometric town, sprites, traffic and animation | [MIT](https://cdn.jsdelivr.net/npm/phaser@3.80.1/LICENSE.md); complete notice included in `static/assets/vendor/Phaser-MIT-LICENSE.txt` |
| jsDelivr | Pinned Phaser CDN distribution | [Phaser distribution URL](https://cdn.jsdelivr.net/npm/phaser@3.80.1/dist/phaser.min.js); Phaser's MIT license applies to the library |
| Inter | Interface type | [SIL Open Font License 1.1](https://github.com/google/fonts/tree/main/ofl/inter); included `static/assets/fonts/inter-OFL.txt` |
| Press Start 2P, CodeMan38 | Town and Demo labels | [SIL Open Font License 1.1](https://github.com/google/fonts/tree/main/ofl/pressstart2p); included `static/assets/fonts/press-start-OFL.txt` |
| Google Fonts | Font distribution and local copies | Individual fonts retain the OFL licenses above |
| Cytopia contributors, including Kingtut 101, RockFort, Yusuf8a684 and the artists named per file | **Current city:** 31 original building, park, road, ground, tree and street-light PNG sheets, imported at revision `c70bbce3ba8b0ba23b8dcce9ff8bc8df0af971f8` | [GNU GPL version 3](https://github.com/CytopiaTeam/Cytopia/blob/c70bbce3ba8b0ba23b8dcce9ff8bc8df0af971f8/license.txt). Unchanged source sheets, full upstream credits, licence and per-file provenance are included under `static/assets/cytopia/`. |
| Kenney Isometric Tiles City | Earlier prototype park base and trees, retained as legacy assets | [CC0 1.0 Universal](https://kenney.nl/assets/isometric-tiles-city); included source license |
| Kenney Isometric Buildings #1 | Earlier prototype building bases and roof, retained as legacy assets | [CC0 1.0 Universal](https://opengameart.org/content/isometric-buildings-1); included source license |
| Kiraku pixel adaptations, Pelita, NPCs, cars, upgrade designs and landscape | Original pixel sprites, code-drawn floor-by-floor buildings, sky, clouds, lake and jetty; reused Cytopia sprites retain their own source credits | CC0 1.0 Universal; `static/assets/pixel/LICENSE.txt` |
| pytest 8.3.4 | Offline maths and API tests | [MIT](https://github.com/pytest-dev/pytest/blob/8.3.4/LICENSE) |
| Playwright 1.58.0 | Browser acceptance checks and screenshots | [Apache-2.0](https://github.com/microsoft/playwright/blob/v1.58.0/LICENSE) |
| Google Chrome | Browser used for the supplied screenshots | [Google Chrome terms](https://www.google.com/chrome/terms/); no browser binary is distributed |
| Pillow 12.2.0 | One-time sprite preparation during development | [MIT-CMU](https://pillow.readthedocs.io/en/stable/about.html#license); not needed to run the app |
| google-generativeai 0.8.5 / Gemini | Optional narration rewrite integration | [Apache-2.0 SDK](https://github.com/google-gemini/generative-ai-python); Gemini service terms apply separately. No live Gemini call was used for this build. |
| Codex, OpenAI | Coding, original pixel preparation, tests, visual review and documentation assistance | Proprietary AI service; output is delivered in this project |
| Claude, Anthropic | Named here because the brief explicitly requested it in credits | **Not used in this build.** No Claude-generated artifact is represented as having been used. |

The Python runtime provides `fractions`, `random`, `json`, `datetime`, `sqlite3`, and other standard-library modules. Flask installs its normal transitive dependencies; their licenses remain with their distributions. This is plain HTML, CSS and JavaScript, with no React or other game framework.

The fictional Kiraku name, business names, street names and pupil labels are demonstration content. The name has not been checked for trademarks.
