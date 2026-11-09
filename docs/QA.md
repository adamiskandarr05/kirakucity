# Validation and visual review

## Requested game checks

- **61 pytest tests pass**, with no network or API key. The suite covers 200 generated seeds per template, verifier rejection rules, hint answer protection, issue scheduling, mastery streaks, outcomes, town changes, trace persistence, step order and duplicate submissions.
- Four city-specific tests verify all original Cytopia PNG hashes, all saved lot footprints and frame indexes, non-overlapping lots, repeat-safe database opening, and expansion of a legacy city without losing a funded case or its calculation.
- **40 Playwright screenshots** cover every screen at 1440 × 900 and 390 × 844, including three hint levels, rejected and verified working, expanded raw trace, the result, a building during its 600 ms growth, the funded-building calculation, the teacher report, the skyline and a whole-city overview.
- The browser report records **101 passing checks**, including district navigation, no click-through behind controls, zoom, all 118 saved lots rendered, no horizontal page overflow, 14px rendered map labels, label collisions before and after construction, trace rows matching saved decisions, traffic, construction, and reduced motion for both people and cars.
- Additional town captures check 1024, 768 and 320 pixels. Browser checks block external requests, exercising the bundled Phaser and font copies. Temporary QA databases leave the live pupil's saved progress untouched.

The authoritative browser results are in [visual-qa.json](visual-qa.json). Source and licence records are in `kiraku/static/assets/cytopia/`. The screenshot index is in the README.

## Visual review

The city now fills the view at neighbourhood scale, with 102 starting buildings and 16 mission lots in a 40 × 40 world. The imported artwork distinguishes houses, apartments, tall office buildings, parks and shop buildings. The main case neighbourhood retains readable labels in the selected language; hovered and selected buildings show their names. Phone district controls use a collapsible menu and keep the map above the independently scrollable case panel.

The interface uses solid backgrounds. Main reading text is at least 17px. The main colour checks meet AA: panel text 11.37:1, muted text 6.97:1, action text 8.68:1, correct text 5.79:1, rejected text 4.58:1, and trace information 7.49:1. Labels have a dark outline and a constant 14px rendered size at every camera zoom.

A construction capture exposed clipped pixel-font labels after repeated state updates. Labels now use shared, immutable bitmap textures drawn after the bundled font has loaded, avoiding repeated destruction and recreation of live text canvases. Construction and post-construction screenshots were regenerated after the correction.

There are **no open failures in the requested automated game checks**. The optional live Gemini rewrite is untested against the real service; failure and no-key fallbacks are tested. Day/night tinting is omitted, as allowed by the brief.

## Additional landing-page style findings

An additional presentation-site layout checker previously returned `GATE: FAIL 16`. These findings remain recorded in [landing-style-check.json](landing-style-check.json); they are separate from the game acceptance results above. They concern its expected marketing-page scaffold: a single-line brand, its particular entrance marker and decorative moment, exact viewport-height sections and footer, and its `.wrap` container conventions. The compact Demo footer and application header were retained for the requested game interface. No passing result from that checker is claimed.

## HUD, camera, avatar, demo and language update

The update adds five backend tests for repeat-safe demo preparation, genuine verified funding, language changes retaining the same case and original audit rows, Malay feedback and answer-safe hints, all four translated templates, and the saved language cookie across pages. All 57 tests pass.

The additional browser suite records **168 passing checks**, **11 new screenshots** and no browser errors. It checks English and Bahasa Melayu at 1886 x 782, 1440 x 900, 1280 x 720, 1024 x 768, 768 x 1024, 812 x 500, 390 x 844 and 320 x 844. The HUD, expanded phone navigation, minimap, case trace, Pelita speech and name are checked for collisions, and controls fit the window height. The short desktop layout compresses the bottom guide and scrolls the district menu.

The camera checks cover drag travel, release momentum and interpolated zoom settling. Repeated identical state reuses all 118 building objects. One headless browser sample at 1440 x 900 measured a median animation frame interval of 6.9 ms and a 95th percentile of 7.1 ms; these are local observations, not a device performance guarantee.

The suite also opens Pelita by clicking the town sprite, checks every displayed activity ID against saved decisions, exercises motion settings, switches language with a typed answer, generates teacher reports in both languages, and repeats demo preparation through Settings. Eight fictional completed cases include verified answers, a misconception and hint, a scheduled revisit, funding decisions and a teacher report. Existing progress is retained.

Report: [update-qa.json](update-qa.json). The original full solve/build flow also passes all 101 checks with 40 screenshots. There are 51 screenshots and 269 passing browser checks across the two suites. The separate landing-style findings above remain recorded; this update does not claim to pass that marketing-layout checker.

## Visible upgrades and landscape validation

Four new backend tests verify safe land/water placement, targeted upgrades through five saved levels, strictly increasing design heights, unchanged footprints and building counts during upgrades, replay-safe finish requests, exact logged funding effects, pupil ownership, required verification and lossless version-2 landscape migration. The current suite has **61 passing tests**.

`world_qa.py` adds **46 passing browser checks** and **12 screenshots**. It builds a taxi stand through the actual interface and upgrades it to levels 2, 3 and 4 on desktop and phone, checking a different texture and greater height at every stage. It measures brighter grass, checks the irregular lake and cloud backdrop, navigates to the lake, and verifies Pelita's route uses the road network around water. Labels and HUD checks are retained in the other suites. The rendered result is inspected visually in the corresponding screenshots.

The phone regression exposed browsers suppressing animation-frame callbacks after startup. Phaser now uses its supported 60 Hz timer fallback; the full play loop, traffic, construction and reduced-motion checks were rerun. Minimap labels use immutable bitmap textures to prevent clipped glyphs. Upgrade notifications use the existing guide card and foreground buildings fade when they obstruct a selected upgrade.

The saved local town was backed up before migration. A before/after comparison verified every pupil, mastery, session, case, attempt, issue and log row unchanged, and every town field except its layout coordinates unchanged. Pupil A retains eight completed cases and 118 town lots.

Current reports: `visual-qa.json` (101 checks), `update-qa.json` (168 checks), and `world-qa.json` (46 checks): **315 browser checks and 63 screenshots** in total. The separate historical marketing-style findings remain documented above.
