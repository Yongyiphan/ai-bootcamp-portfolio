# Day 8 Lab V2 Completion Checklist

## What changed from V1

Question 2 is substantively unchanged. V2 expands and clarifies Question 1 by requiring direct container verification, use of the supplied Jenkinsfile, reviewed test selection, sanitized AI diagnosis input, restoration of the correct code, and a final Jenkins SUCCESS after restoration.

## Question 1

- [x] Docker Compose and Jenkins configuration match V2.
- [x] Flask container compiles Linux `/app/multiply` at startup.
- [x] Flask screenshot captured.
- [x] Initial Jenkins SUCCESS captured.
- [x] Four additional AI-proposed cases reviewed and added.
- [x] Intentional failure screenshot and console output captured.
- [x] Failure output sanitized in the documented AI diagnosis.
- [x] Different-prompt review of C++ and Python documented.
- [x] Correct `a * b` implementation restored.
- [ ] Run final Jenkins build with all eight tests and capture SUCCESS.
- [x] Direct container check captured: `/app/multiply 3 4` returned `12`, and all eight cases passed.

## Question 2

- [x] Data-driven parsing and validation.
- [x] Dijkstra pathfinding using edge distance.
- [x] SVG visualization and route highlighting.
- [x] Public pathfinding and protected editing.
- [x] Node and edge CRUD operations.
- [x] Sixteen automated behavioral tests passing locally.
- [x] Three alternative AI-generated test maps.
- [x] Required AI review notes.
- [ ] Capture map, path-result, and authentication screenshots.
- [ ] Capture command-line or Jenkins verification evidence.

## Final integrity

- [ ] No password, token, `.env`, or Jenkins home data submitted.
- [ ] Submitted `multiply.cpp` contains multiplication, not the intentional bug.
- [ ] Evidence filenames match `docs/ci_result_summary.md`.
