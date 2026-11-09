# Kiraku: City Planner

**Kira, bina, selesaikan (Count, build, solve).** A personal, local Flask game for secondary students, with a living pixel town, four linked maths templates, and saved agent decisions. Bandar Kiraku and every pupil, business and street are fictional.

## Run locally

Python 3.11 or newer is required. There is no JavaScript build step.

```powershell
# Open a terminal in the project folder containing this README.
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m flask --app kiraku.app run
```

Open [the landing page](http://127.0.0.1:5000/), [pupil selection](http://127.0.0.1:5000/play), or [the teacher desk](http://127.0.0.1:5000/teacher). To open the city directly with Pupil A, use [this demo link](http://127.0.0.1:5000/play?pupil=pupil-a). Use the avatar at the top right to change pupils. On a phone, drag the map to look around; the building list gives a keyboard-accessible alternative.

Progress is stored in `instance/kiraku.sqlite`. `KIRAKU_DATABASE` selects a different SQLite file, and `KIRAKU_SECRET_KEY` can provide a stable cookie secret across server restarts. This is a local fictional demo, without login or a production hosting setup.

## The expanded Cytopia city

The city uses **original Cytopia PNG artwork**, imported directly from [Cytopia's repository](https://github.com/CytopiaTeam/Cytopia), pinned to revision `c70bbce3ba8b0ba23b8dcce9ff8bc8df0af971f8`. It is a 40 × 40 tile world with **102 starting buildings**, **16 buildable plots**, and **four districts**. Housing, offices, public gardens, trees, roads and mission buildings are drawn from the saved city layout. This replaces the earlier 12 × 12 town.

- Drag the map or use arrow/WASD keys to pan. Scroll or use +/− to zoom.
- The district buttons travel to the town centre, residential quarter, civic skyline and garden district.
- Click the minimap to travel, or use the grid button to see the whole city. The centre button returns to the town centre.
- [Open the city directly](http://127.0.0.1:5000/play?pupil=pupil-a&city=1). A pending case stays available through **Continue case** (or **Sambung kes** in Bahasa Melayu).
- Existing databases expand automatically. Pupil progress, open issues, case histories and building funding links are preserved. Further correct cases fill empty plots before upgrading a built one.

The source PNG sheets are unmodified. `static/assets/cytopia/manifest.json` records each artist, upstream path, frame size and SHA-256 hash. Original sheets, extracted preview frames, upstream credits, the GPL-3.0 licence and a notice are included. Only Cytopia's artwork is imported; Kiraku continues to use Flask, SQLite and Phaser for its application and maths-driven map.

## Smooth map, Pelita and settings

The map uses eased dragging, release momentum and smoothly anchored zoom. It reuses unchanged buildings and static scenery, refreshes labels and depth order less often, and skips offscreen objects. Reduced motion removes momentum and background animation. The HUD measures the actual headings, controls and bottom dock, keeping the district panel and minimap clear of them. On phones, open **Districts** for the district and building lists.

Pelita is a visible owl on the town roads. The owl toolbar button finds her. Click her town avatar to inspect the latest five saved agent actions. Her movement and speech respond to actual case and decision-log events; they do not invent conversations or imply a live language model.

Use **Settings ⚙ → Language** to choose **English** or **Bahasa Melayu**. This applies to the town, cases, hints, feedback, outcomes, pupil selection and teacher report, and is remembered on this browser. Changing language retains the current case and typed answer. Original audit records remain unchanged; the visible agent summaries are localized.

Use **Settings → Prepare demo progress** to complete eight cases for fictional Pupil A. It submits checked answers through the normal game API, including an initial misconception, a hint, a later revisit, funding decisions and a teacher report. It keeps existing progress and adds only enough cases to reach eight, so repeating it does not duplicate history. The current local demo is already prepared. The ZIP excludes the local database; use this button after starting a fresh copy.

## Visible building upgrades and a brighter landscape

Every earned building level now has a visibly taller design. Level 1 retains its Cytopia artwork. Level 2 and above use original code-drawn Kiraku designs, adding another floor per level, category-specific frontage, rooftop planting, solar details and later roof features. The footprint stays inside the saved lot. Parks gain a planted pavilion. The building name and street are retained during upgrades.

Open a mission building from the map or Building list and choose **Upgrade this building**. Quest records the selected building and prepares its matching mathematics case. A case already in progress is resumed first. All steps must still be verified and the funding target met; a held project does not gain a level. Automatic Next case selection continues to fill empty mission plots before upgrading existing ones. Building counters count buildings, rather than treating extra floors as additional buildings.

The seeded landscape has irregular road blocks, scattered lot placement, clustered trees and flowers, brighter grass, an uneven island coast and **Cloud Lake / Tasik Awan**, with a timber jetty and lily pads. **Visit the lake** travels to it. The whole-city view shows the island against a blue sky and moving clouds. Pelita follows the connected road network around the water. Existing town IDs, levels, cases, funding links and open issues survive the layout migration.

The map uses a steady 60 Hz timer fallback so phones keep animating when browser paint callbacks are suppressed. Selected upgrades remain visible through foreground buildings. Town notifications use Pelita's existing card, and minimap text uses immutable bitmap labels.

Browser evidence for four visible stages, lake navigation, grass brightness and safe paths is in [world-qa.json](docs/world-qa.json). Run `python tools/world_qa.py --chrome "C:\Program Files\Google\Chrome\Application\chrome.exe"` to reproduce it.

## Tests and screenshots

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe tools/visual_qa.py
```

If Chrome is already installed, the browser check can use it instead:

```powershell
.\.venv\Scripts\python.exe tools/visual_qa.py --chrome "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

The automated maths and API suite contains **61 passing tests**, including **200 seeds for each of the four templates**, original Cytopia file hashes, city footprints and preservation of a funded case during migration. The browser check uses temporary databases, blocks external network requests, and checks the complete play loop at 1440 × 900 and 390 × 844. It also checks district navigation, zoom, the city overview, reduced motion and town layouts at 1024, 768 and 320 pixels. It does not modify your saved town.

Browser evidence: [visual-qa.json](docs/visual-qa.json) and [update-qa.json](docs/update-qa.json). Run `python tools/update_qa.py --chrome "C:\Program Files\Google\Chrome\Application\chrome.exe"` for the language, avatar, demo, camera and HUD checks at eight window sizes in both languages. Visual review notes: [QA.md](docs/QA.md). The building animation captures freeze the real 600 ms tween at approximately 220 ms, then resume it. The landing image is a real capture of the Phaser canvas, without interface overlays.

| Screen | Desktop | Phone |
| --- | --- | --- |
| Landing | [1440](docs/screenshots/01-landing-1440.png) | [390](docs/screenshots/01-landing-390.png) |
| Pupil selection | [1440](docs/screenshots/02-pupil-select-1440.png) | [390](docs/screenshots/02-pupil-select-390.png) |
| Town | [1440](docs/screenshots/03-town-1440.png) | [390](docs/screenshots/03-town-390.png) |
| Case brief | [1440](docs/screenshots/04-case-brief-1440.png) | [390](docs/screenshots/04-case-brief-390.png) |
| Working and locked steps | [1440](docs/screenshots/05-working-1440.png) | [390](docs/screenshots/05-working-390.png) |
| Rejection and open issue | [1440](docs/screenshots/06-rejected-1440.png) | [390](docs/screenshots/06-rejected-390.png) |
| Hint 1 | [1440](docs/screenshots/07-hint-1-1440.png) | [390](docs/screenshots/07-hint-1-390.png) |
| Hint 2 | [1440](docs/screenshots/07-hint-2-1440.png) | [390](docs/screenshots/07-hint-2-390.png) |
| Hint 3, worked answer | [1440](docs/screenshots/07-hint-3-1440.png) | [390](docs/screenshots/07-hint-3-390.png) |
| Expanded raw trace | [1440](docs/screenshots/08-trace-raw-1440.png) | [390](docs/screenshots/08-trace-raw-390.png) |
| All steps verified | [1440](docs/screenshots/09-verified-1440.png) | [390](docs/screenshots/09-verified-390.png) |
| Outcome and Pelita review | [1440](docs/screenshots/10-result-1440.png) | [390](docs/screenshots/10-result-390.png) |
| Building mid-growth | [1440](docs/screenshots/11-building-animation-1440.png) | [390](docs/screenshots/11-building-animation-390.png) |
| Updated town | [1440](docs/screenshots/12-town-grown-1440.png) | [390](docs/screenshots/12-town-grown-390.png) |
| Building funding calculation | [1440](docs/screenshots/13-building-funding-1440.png) | [390](docs/screenshots/13-building-funding-390.png) |
| Teacher desk and report | [1440](docs/screenshots/14-teacher-1440.png) | [390](docs/screenshots/14-teacher-390.png) |

Additional captures: [reduced motion](docs/screenshots/15-reduced-motion-1440.png), [1024](docs/screenshots/16-responsive-town-1024.png), [768](docs/screenshots/16-responsive-town-768.png), [320](docs/screenshots/16-responsive-town-320.png).

Expanded city: [Cytopia skyline, desktop](docs/screenshots/17-cytopia-skyline-1440.png), [skyline, phone](docs/screenshots/17-cytopia-skyline-390.png), [whole-city overview, desktop](docs/screenshots/18-city-overview-1440.png), [overview, phone](docs/screenshots/18-city-overview-390.png).

## Original fresh-start walkthrough with Pupil A

Use a fresh database for the fixed starting numbers. To preserve an existing town, set `KIRAKU_DATABASE` to a new filename before starting the server.

1. **0:00–0:40 — Choose a planner.** Select Pupil A. Explore the original Cytopia buildings: houses, taller offices, shops, public gardens and empty plots. Use a district button or the minimap, then return to the centre. Seven people and three cars move along the roads. The case-building counters start with three shops, one stall, one park and one stand; the wider starting city has 102 buildings.
2. **0:40–1:20 — Read the decision.** Click **Kes seterusnya (Next case)**. Scroll the agent trace to Quest. It selects reverse percentages because Pupil A starts at 25% mastery in that topic. Follow the amber pulse to the flower-shop plot. Read the given increase, discount, selling price, cost and profit target.
3. **1:20–2:10 — Take the trap.** Start calculating. Enter **108.00**, then **Semak**. The rejection names the successive-percentage mistake. The town count stays unchanged; the plot gets an amber flag. Open hints 1 and 2; neither contains the answer. Expand the Feedback trace row to inspect the submitted value.
4. **2:10–3:10 — Verify the plan.** Enter **110.00** for the original price. The next step opens. Enter **33.80** profit. Finish the case and read the outcome, step marks and Pelita review. Return to town: the flower shop grows over 600 ms, dust clears, and its sign lights up. Shops increases from three to four.
5. **3:10–4:00 — Inspect the funding.** Open **Senarai bangunan (Building list)**, choose Kedai Bunga Melur, and inspect the saved calculations. Pause the town with the motion control, then resume it.
6. **4:00–5:00 — See the teacher view.** Open **Guru (Teacher)**, inspect the open issue and mastery changes, and generate Pupil A's three-section report. The issue is due after two completed cases; correcting the original case does not erase the need for later practice.

Extended revisit: finish the next case using its hints if needed. Quest then returns to the percentage issue. Completing that later practice case resolves the old issue. A park with a positive shortfall remains unfunded even when every answer is correct; the result explains this branch.

## How it works

- `kiraku/state.py` owns every SQLite operation. Agents receive a state interface and never write SQL. Immediate transactions make checks and finish operations atomic.
- `kiraku/cases/templates.py` owns generation, exact solutions, misconception values, rounding, briefs, and outcome rules. All mathematical arithmetic uses `fractions.Fraction`; half-up rounding occurs for display and answer checking only.
- Quest chooses due issues first, then weakness plus a small deterministic exploration bonus. A cooling-down issue is excluded until two cases have been completed. Three consecutive correct steps raise the practice level; two consecutive wrong steps lower it. The fixed template level remains visible on each brief.
- Scenario uses fixed fictional names. Problem computes answers in code. Verifier checks consistency, positivity, percentages, unique mode, rounding, and distinct misconception answers. Three rejected generation attempts trigger a verified default; every rejection is logged.
- Feedback records a checked attempt and creates at most one open issue per case step. Submission IDs provide replay protection; already-verified steps return their first accepted result without changing mastery, town or logs.
- Hint levels come directly from the step's three-part solution text. Only level 3 contains the worked answer. The API withholds expected values and trap values from unseen steps.
- Outcome changes a building only after all steps have been verified and the project's funding rule succeeds. Repeated finish requests return the saved result. A failed funding target leaves the town unchanged.
- Phaser draws all buildings from `town`, and all waiting flags from `open_issues`. `kiraku/city.py` defines the saved district layout; `static/js/city-scene.js` renders the original Cytopia sheets. Initial terrain and roads are fixed map infrastructure. HTML communicates with Phaser through `static/js/bus.js` and the JSON API. The trace displays only rows from `decision_log`, newest first.
- Initially built buildings are identified as starting-town buildings. They have no invented pupil funding calculation; later upgrades link to the actual case that funded them.
- The map's labels retain a 14px rendered size at every zoom. Labels appear on central landmarks, focused lots and hovered buildings; the building list exposes every name and status. NPCs, cars, pulses and construction respect reduced motion.

## Optional Gemini narration

The complete game and teacher report work without an API key. The footer says **Pelita · local guide** when no key is configured. Narration and teacher reports use templates by default.

To try optional narration rewrites, install `google-generativeai==0.8.5` separately and set `GEMINI_API_KEY` in the environment. `GEMINI_MODEL` can select a compatible model. The key is never saved in project files, responses, or the decision log. SDK errors, unavailable models, long text, markup, or numeral-containing rewrites fall back to the template. Each Pelita decision records which source was actually used. No live Gemini call was used for this build or its tests.

```powershell
$env:GEMINI_API_KEY = "your-own-key"
.\.venv\Scripts\python.exe -m flask --app kiraku.app run
```

## API

Page routes: `GET /`, `/play`, `/teacher`.

Data routes: `GET /api/pupils`, `GET /api/pupil/<id>/state`, `POST /api/session/start`, `POST /api/case/next`, `POST /api/case/step`, `POST /api/case/hint`, `POST /api/case/finish`, `GET /api/case/<id>/why`, `GET /api/events?since=<id>`, `POST /api/teacher/report`. `GET /api/teacher/state` supplies the teacher screen. Start a session before pupil case operations. Case mutations use the session's pupil; another pupil's case is rejected.

Example step body:

```json
{"case_id":"returned-case-id","step_index":0,"value":"110.00","submission_id":"unique-attempt-id"}
```

## Art, credits and limits

Art source and mappings: [ART.md](docs/ART.md). Framework, font, asset and AI credits: [CREDITS.md](CREDITS.md).

[Phaser 3.80.1](https://phaser.io/download/release/v3.80.1) was released on 27 February 2024 and verified before use, well over two weeks before this build. The page loads this exact version from jsDelivr, with a bundled copy for outages or offline play. Google Fonts are requested normally and also bundled locally with their licenses. Only Phaser is used as a game framework.

**The Kiraku name has not yet been checked for trademarks.** No leaderboard, ads, purchases, punitive timer, game-over state, real pupil data or government data is included. Day/night tinting is omitted because it is optional.

## Updated demo screenshots

- [Town, desktop English](docs/screenshots/19-town-polished-1886-en.png)
- [Town, phone Bahasa Melayu](docs/screenshots/19-town-polished-390-ms.png)
- [Pelita activity](docs/screenshots/20-pelita-activity.png)
- [Language settings, English](docs/screenshots/21-settings-390-en.png) · [Bahasa Melayu](docs/screenshots/21-settings-390-ms.png)

New landscape and upgrades: [island overview](docs/screenshots/22-lake-island-1440.png), [lake](docs/screenshots/23-lakeside-1440.png), [level 1](docs/screenshots/24-building-level-1-1440.png), [level 2](docs/screenshots/24-building-level-2-1440.png), [level 3](docs/screenshots/24-building-level-3-1440.png), [level 4](docs/screenshots/24-building-level-4-1440.png). Team handover: [TEAM-HANDOVER.md](docs/TEAM-HANDOVER.md).
