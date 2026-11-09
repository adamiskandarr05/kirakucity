# Kiraku: City Planner — team handover

Repository: https://github.com/adamiskandarr05/kirakucity
Current edition: visible building upgrades and landscape update on `main`
Prepared: 9 November 2026

## Project overview

Kiraku: City Planner is a browser-based mathematics learning game for secondary students, especially Form 3–4. Its idea is **“Kira, bina, selesaikan” — count, build, solve.** Students solve linked mathematics cases to help develop the fictional Bandar Kiraku. Their answers produce visible consequences: a business can open, a taxi stand can be funded, or a park can remain on hold because its budget is insufficient.

The project combines a city exploration game, adaptive practice, step-by-step checking, a visible guide called Pelita, and a teacher dashboard. All pupil profiles, businesses, streets and demonstration progress are fictional.

## What students do

1. Choose one of three fictional pupil profiles, each with different starting mastery scores and its own saved progress.
2. Explore the city and request the next mathematics case.
3. Read the scenario, given values, units and rounding instructions.
4. Submit answers in order. A verified step unlocks the next step.
5. Request progressively stronger hints when needed.
6. Finish the case and see whether the project meets its funding rule.
7. Return to town to see the resulting improvement, then inspect the building's verified funding calculations.

The four implemented case families are:

| Case | Mathematics | Decision in the town |
| --- | --- | --- |
| Flower shop | Successive percentages, original price and profit | Open the shop when profit reaches its target |
| Taxi stand | A linear fare equation with a fixed fee and distance rate | Fund the stand after the linked calculations are verified |
| Garden stall | Mean, total, missing sales and mode | Open the stall when its mode meets the sales target |
| Neighbourhood park | Two linked dimensions, perimeter, fencing cost and budget shortfall | Fund the park when the shortfall is zero |

Correct answers do not automatically mean a project is financially viable. A student can calculate a positive park shortfall correctly and receive a verified result while the park remains on hold. This makes the distinction between mathematical correctness and the resulting planning decision visible.

## What the agentic AI does

The current implementation is a **bounded, rule-based agent workflow**. Specialized software agents read saved pupil information, choose actions, check results and record their decisions. Most behavior is deterministic Python logic. There is no continuously running, self-directed language model managing the town.

The agentic element is the coordinated loop: **observe progress → choose practice → prepare and verify a case → evaluate the student's work → update progress and town state → revisit weaknesses later.**

| Agent | Responsibility |
| --- | --- |
| Quest | Chooses the next case using saved topic mastery, previous practice and open issues. Due revision issues take priority; otherwise weaker and less-practised topics receive preference. |
| Scenario | Adds fictional business names and streets to place the mathematics in the town. |
| Problem | Generates values within the four supported templates and calculates expected answers and common misconception values using exact fractions. |
| Verifier | Checks generated cases for mathematical consistency and constraints, and checks submitted answers. Generation retries up to three times before using a verified default. |
| Feedback | Explains accepted or rejected steps, recognizes predefined misconception answers, updates mastery and records an issue for later revision. |
| Hint | Provides three levels of help: an approach, a method, then a worked solution. The first two levels do not reveal the numerical answer. |
| Outcome | Applies the project's funding rule after every step is verified. It determines whether to build or hold the project; the state layer saves the resulting change. |
| Pelita | Presents encouragement, the case review and visible town activity. The owl's movement and speech reflect actual saved agent events. |
| Teacher | Produces a three-part report covering progress, attention areas and next steps from saved mastery and issues. |

Quest does not choose cases randomly without regard to the pupil. It prioritizes issues whose revision deadline has arrived and otherwise scores topics using weakness and a small bonus for less practice. Wrong answers create revision issues with a two-completed-case threshold. Correcting the original case does not immediately remove the need for a later revisit.

Three consecutive correct checked steps increase the saved practice level; two consecutive wrong checked steps decrease it. The four question templates retain their defined levels and structures. This is adaptive selection within a small curriculum, rather than an unlimited AI-generated question bank or a trained model learning from pupils.

Every agent action is stored in `decision_log`, with the agent name, relevant pupil/case, input summary, decision, structured evidence and timestamp. The activity panels display these records. They do not invent background conversations or reasoning. Localized display summaries leave the original audit records intact.

## Pelita and optional generative AI

Pelita is a visible owl avatar on the town roads. The owl toolbar button finds her, and clicking her town avatar opens the latest five saved agent actions. She gives the agent workflow an understandable presence inside the game.

The complete game works without an AI API key. In its default mode, encouragement, hints, feedback and reports come from the project's templates and rules.

An optional Gemini integration can rewrite short encouragement or review narration. It is not responsible for choosing correct answers, grading work, changing mastery or approving town funding. The rewrite request receives encouragement text, rather than the expected mathematical answers. Narration is checked for length, numerals and markup, with a template fallback when the service fails or returns unsuitable text. The live Gemini service was not used in the delivered demo's testing.

For a presentation, an accurate description is: **“Kiraku uses specialized agents to adapt the practice sequence, verify calculations, give staged support and connect verified work to town development. Pelita makes their saved activity visible. The core decisions work locally through explicit rules, with optional AI assistance for narration.”**

## Visible upgrades and the landscape update

Mission buildings now gain a visibly taller design at every earned level. Level 1 keeps the original Cytopia sprite; later levels have original code-drawn floors, category-specific facades and rooftop details. Parks gain a planted pavilion. The lot footprint, building name and street remain stable during upgrades. A held funding outcome does not gain a level.

Students can open a mission building and choose **Upgrade this building**. Quest logs the selected building and creates the matching mathematics case. An existing active case is resumed first. Normal automatic selection still fills empty plots before upgrading built ones. Building counters now count buildings, so an extra floor does not invent another shop or stand.

The city now has seeded scattered placement, uneven road blocks, clustered trees and flowers, brighter grass, an irregular island coast, Cloud Lake / Tasik Awan with a jetty and lily pads, and a blue sky with clouds. **Visit the lake** navigates there. Pelita follows connected roads around the water, and the whole-city overview reveals the island. Migration preserves saved history, funding and levels.

## City and interface

The city is a 40 × 40 isometric map, initially containing 102 built lots and 16 mission lots across four districts: town centre, residential quarter, civic skyline and garden district. Houses, apartments, offices, gardens, shops, trees and roads give it the scale of a neighbourhood rather than a small isolated board. Seven walking NPCs and three moving cars add activity.

The current city uses 31 original Cytopia PNG sprite sheets, imported from a pinned upstream revision. The artwork is reused directly. Cytopia's C++ simulation engine was not imported; Kiraku's gameplay, mathematics, database and Phaser renderer are implemented separately. Source records, artist credits and license files are included in the repository.

Map controls include dragging with eased movement and release momentum, smoothly anchored zoom, keyboard panning, district travel, a minimap, a whole-city overview and a centre button. The renderer reuses unchanged buildings and static scenery, reduces repeated label/depth work and skips offscreen objects.

The interface measures its actual panels to separate the district list, map controls, minimap, guide card and action button. Short desktop windows use a more compact guide; phones use collapsible district navigation. Motion can be paused, and reduced-motion preferences are respected.

Settings offers **English** and **Bahasa Melayu**. The choice applies to pupil selection, town controls, cases, hints, feedback, results and teacher reports, and is remembered in the browser. Switching language preserves the current case and typed answer.

## Teacher view and saved data

The teacher dashboard shows topic mastery, checked-step counts, practice levels, open revision issues, saved decision logs and a three-section practice report. Funded buildings link back to the case and verified calculations that produced the improvement. Starting-town buildings are identified separately and do not have invented pupil funding histories.

SQLite stores pupil profiles, mastery, sessions, cases, submitted steps, open issues, town lots and decision logs. The normal local database is `instance/kiraku.sqlite`. Language and motion preferences are held in the browser. Duplicate submissions and repeated finish requests are handled without awarding progress or funding twice.

## Technical handover

| Area | Implementation / main location |
| --- | --- |
| Server and page/API routes | Python 3.11+, Flask; `kiraku/app.py` |
| Persistence | SQLite; all SQL centralized in `kiraku/state.py` |
| Agent logic | `kiraku/agents/` |
| Question generation and exact mathematics | Python `Fraction`; `kiraku/cases/templates.py` |
| City layout, landscape and upgrade metadata | `kiraku/city.py`, `kiraku/landscape.py`, `kiraku/progression.py` |
| Town, camera, traffic, avatar and visual designs | Phaser 3.80.1; `city-scene.js`, `landscape-scene.js`, `building-designs.js` |
| Student interaction | Plain HTML/CSS/JavaScript; `play.js` and templates |
| Panel layout and settings | `hud-layout.js`, `settings.js`, `app.css` |
| Language presentation | `kiraku/i18n.py` and `static/js/i18n.js` |
| Demo preparation | `kiraku/demo.py` |
| Automated checks and browser evidence | `tests/`, `tools/`, `docs/` |

There is no React application or JavaScript build step. Local copies of Phaser and the fonts provide fallbacks when external loading is unavailable.

To run on Windows, install Git and Python 3.11 or newer, then:

```powershell
git clone https://github.com/adamiskandarr05/kirakucity.git
cd kirakucity
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m flask --app kiraku.app run
```

Open `http://127.0.0.1:5000`. The GitHub repository contains the source; it is not a hosted playable deployment. A localhost address works on the machine running the application.

## Demonstration handover

The existing local Pupil A demo has eight completed cases. On another machine or a fresh database, use **Settings → Prepare demo progress**. The preparation submits answers through the normal checking and completion APIs. It includes a misconception, a hint, a later revisit, town funding decisions and a teacher report. It preserves existing progress and adds only enough cases to reach eight, so repeating it does not duplicate the history. The local database is not committed to GitHub.

A useful demonstration sequence is:

1. Open Pupil A's town and show the saved completed-case count.
2. Pan, zoom and switch districts.
3. Find Pelita and click her to show genuine saved agent activity.
4. Open a funded building and show its verified calculation history.
5. Start the next case, explain Quest's selection, then demonstrate ordered steps and hints.
6. Switch between English and Bahasa Melayu in Settings.
7. Open the teacher dashboard and generate a report.

The fixed flower-shop example in the README belongs to a **fresh-start** database: an original price of RM110 becomes RM118.80 after a 20% increase and 10% discount; with RM85 cost, profit is RM33.80, exceeding the RM25 target. The prepared eight-case demo has later generated values, so those fixed answers should not be reused for its next question.

## Validation and current scope

The delivered version passed **61 automated tests**, including 200 generated seeds for each of the four question templates. It also passed **315 browser acceptance checks**, with **63 screenshots** covering the play flow, construction, funding history, teacher reports, English/BM, responsive layouts, avatar activity, motion and camera behavior.

The project is a local demonstration with fictional profiles, four defined mathematics templates and explicit agent rules. It does not currently provide real pupil accounts, school-level access control, multiplayer, a hosted production service, free-form AI tutoring or a full city economy simulation. Optional live Gemini narration remains unverified against the real service. A separate marketing-page style checker recorded 16 scaffold-related findings; these remain documented in `docs/QA.md` and are separate from the passing game acceptance checks.

Start with `README.md` for setup and the original walkthrough, `docs/QA.md` for validation and limitations, and `CREDITS.md` / `docs/ART.md` for artwork provenance and licensing records.
