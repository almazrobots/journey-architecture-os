# Rendering a journey system as a map

`scripts/render_map.py` turns the CSV registers of one journey system into a single HTML page: an overview, one poster per mapped journey, a service-system view, and a list of what is still unknown. The renderer reads nothing but the registers defined in [the ontology](../skills/journey-architecture/references/ontology.md). It never parses the Markdown views, so the page cannot say anything the registers do not hold.

```bash
python3 scripts/render_map.py examples/saas-onboarding -o build/saas-onboarding-map.html
python3 scripts/render_map.py path/to/system -o map.html --lang ru --title "Камеральная проверка"
make render    # renders the flagship example to build/saas-onboarding-map.html
```

`build/` is gitignored. Generated pages are not committed next to the examples; publish a rendered page on purpose, not as a side effect of a build.

## What the page shows

| Section | Built from |
|---|---|
| Overview: title, journey hierarchy, evidence meter by journey | journey registry, actor register, evidence register, and the `evidence_status` of every claim in the other registers |
| Poster for each L2 journey that has nodes | actor, journey, node, experience, moment, metric and opportunity registers |
| Service system, one tab per journey state | journey registry, node register, relation register |
| What we don't know | evidence rows with `evidence_status = unknown`, and the nodes, moments, metrics and opportunities that cite them |

**Poster.** A header with an actor card (name, type, segment and context; a monogram, never a stock photo), the journey's trigger, boundaries and desired outcome, its state and version, links to its baseline or to its target and transitional versions, and its root metric. Below it, one column per stage in `sequence` order, episodes nested inside their stage, and one row (band) per kind of content:

1. Actions, touchpoints and channels, expectations, thoughts, pains, workarounds, emotions, questions — from the experience register. Rows on an episode are shown in the stage's column and name the episode.
2. Moments that matter (diamonds), metrics (the journey's `actor-outcome` metric is the highlighted root), opportunities with their decision bucket and the status of both the problem and the root cause.

**Service system.** One lane per actor. The lanes hold the L2 journeys of the selected state plus any journey linked to them in the relation register (a journey from another state is tagged with its state). A journey without nodes appears as a single dashed card: its stages are not mapped. Columns are computed from the relations so that a stage never sits left of what it `depends_on` or of what `enables` it, and `precedes` keeps order within a lane. If relations form a cycle the layout falls back to lane order only. Arrows follow the direction of flow (prerequisite to dependent) and take their line style from the relation's status.

## The status encoding

`evidence_status` is the variable the page is built around. Every stage, episode, experience row, moment, metric, opportunity and relation carries it in three redundant ways, so the page reads without colour and in greyscale print:

| Status | Colour | Pattern | Card border | Label |
|---|---|---|---|---|
| observed | dark blue | solid fill | solid, heavy | "observed" |
| inferred | light blue | diagonal hatch | solid, light | "inferred" |
| hypothesis | amber | dots | dashed | "hypothesis" |
| unknown | grey | empty | dotted | "unknown" |

Evidence IDs are buttons. Hover or keyboard focus shows the finding; Enter or a click opens a side panel with source, sample, collection date and limitations. Metric IDs work the same way.

## Honesty rules for the emotion curve

The emotion band is the one place where a journey map traditionally invents data. The renderer draws only what the experience register holds, under these rules:

1. **Points come only from `emotion` rows.** Each row with a valence is one point at its valence (−2 to 2). Several rows in a stage are spread across the stage's column in node order. Nothing is averaged, smoothed or interpolated.
2. **A stage without emotion rows is a visible gap.** It is outlined and labelled "not measured", and the line stops before it and restarts after it. The line is never carried across a gap.
3. **Line style carries status.** A segment is solid only when both of its points are `observed`. If either point is `inferred` or `hypothesis`, the segment is dashed. Point markers repeat the status: filled (observed), hatched (inferred), hollow with a dashed outline (hypothesis).
4. **`unknown` rows are not plotted.** An emotion row marked `unknown` is listed under the curve as an open question and its stage counts as not measured.
5. **No experience register, no curve.** When `experience-register.csv` is missing, every stage shows the "not measured" gap and a notice says which bands are absent. When the register exists but has no rows for a journey, the poster says so.

The validator already requires that an `observed` or `inferred` emotion row cites evidence from interviews, observation, diaries, surveys or usability tests; documents, analytics and stakeholder input cannot show how someone felt. The renderer does not re-check that rule; run `make validate` first.

## Guarantees

- **Self-contained.** One HTML file, no network requests: fonts are embedded (subsets of Onest, Literata and JetBrains Mono under the SIL Open Font License 1.1; see `scripts/render_assets/fonts/OFL.txt`), SVG is inline, script is inline. The only URL in the output is the SVG namespace string.
- **Deterministic.** The same registers give the same bytes; nothing depends on the clock or the environment.
- **Escaped.** Every register value is HTML-escaped; the JSON data block escapes `<`, `>` and `&`. `tests/test_render.py` appends an HTML payload to every free-text cell and checks that it never reaches the page as markup.
- **Strict on statuses.** A status outside `observed`, `inferred`, `hypothesis`, `unknown`, or an emotion row without a valence from −2 to 2, stops the render with exit code 2 instead of drawing a wrong colour.
- **Accessible.** Keyboard access to every control (tabs with arrow keys, Escape closes panels), visible focus, light and dark themes from `prefers-color-scheme`, phone width without page-level horizontal scroll (posters and the service grid scroll inside their own containers), and print with each poster on its own landscape page.

## Limits

- The renderer shows the model; it does not validate it. A system that fails `validate_repo.py` may render misleadingly.
- Journeys without nodes get no poster. They appear in the index and, when related, as a dashed card in the service view.
- The interface is available in English and Russian (`--lang`); register text is shown as written.
