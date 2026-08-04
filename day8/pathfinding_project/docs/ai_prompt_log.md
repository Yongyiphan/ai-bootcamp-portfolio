# AI Prompt Log

## Session 1: Data format review

**Goal:** Check whether the supplied node and edge files are sufficient and unambiguous.

**Prompt:**

> Review this map data format for a pathfinding system. Check whether the node and edge files contain enough information for shortest-path computation and visualization. Identify missing assumptions, ambiguous fields, invalid references, duplicate IDs, negative distances, comments, and malformed rows.

**AI output summary:** The format is sufficient if edges are explicitly documented as undirected and `Distance` is distinguished from coordinate distance. It recommended rejecting duplicate IDs, invalid references, negative distances, unknown types, and malformed records.

**Human decision:** Accepted these findings. `map_loader.py` performs all of these validations. Names remain restricted to one whitespace-free field because that is the supplied format.

**Verification:** Parser tests cover comments, blank lines, duplicate node IDs, and invalid edge references.

## Session 2: Test-map generation

**Goal:** Demonstrate that the algorithm is data-driven.

**Prompt:**

> Generate three small Node_Info.txt and Graph_Path.txt pairs: a connected graph with multiple routes, a disconnected graph, and a graph with two equally short routes. Include comments and make at least one edge distance differ from coordinate distance.

**AI output summary:** Three compact maps were proposed.

**Human decision:** Reviewed the IDs, references, and expected route costs, then saved corrected versions under `docs/test_maps/`.

## Session 3: Corner-case requests

**Prompt:**

> Generate adversarial shortest-path requests. For each, state the start, end, expected behavior, and why it matters. Include identical endpoints, invalid IDs, isolation, cycles, equal paths, and a lower-cost route that looks longer geometrically.

**AI output summary:** Recommended normal, identical endpoint, invalid start/end, unreachable, multiple-route, cycle, equal-cost, and coordinate-versus-cost cases.

**Human decision:** Implemented the cases with deterministic expected outputs in `tests/test_pathfinder.py` and `tests/test_web.py`.

## Session 4: Authentication review

**Prompt:**

> Act as a strict access-control reviewer. Public users may view the map and find paths. Only authenticated editors may add, update, delete, or persist nodes and edges. Find server routes or UI actions that could bypass this rule. Do not treat hidden UI as authorization.

**AI output summary:** Every mutating HTTP method needs a server-side session check; login comparison should avoid naïve comparison; logout must clear authorization; public GET routes must remain accessible.

**Human decision:** Accepted. All six mutation route variants call the same authorization guard. Password comparison uses `hmac.compare_digest`, and tests exercise every unauthorized mutation route.

## Session 5: Tests and CI review

**Prompt:**

> Review these tests and CI stages. Identify tests that merely execute code, missing behavioral assertions, unreliable oracles, and false confidence. Require evidence for parsing, path cost, error handling, access control, and persistence.

**AI output summary:** The original `test_basic.py` was unrelated to application behavior. Stronger checks require exact expected paths/costs, rejected access, invalid data, and mutation persistence.

**Human decision:** Question 2 now has 16 behavioral tests. Question 1 retains the original smoke test but adds a separate cross-language verifier with valid and invalid cases.

**Known limitation:** CI and tests cannot prove production-grade security or concurrent-write correctness. This is a lab-grade, single-process editor using a shared password.
