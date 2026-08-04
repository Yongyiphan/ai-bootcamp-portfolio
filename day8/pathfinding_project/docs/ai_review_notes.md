# AI Review Findings and Human Assessment

## Data-format review

The two-file format contains enough information for visualization and weighted shortest paths. The following assumptions are now explicit:

- Paths are undirected.
- `Distance` is a non-negative path cost; coordinates are only for plotting.
- Node and edge IDs must be unique.
- Every edge endpoint must identify an existing node.
- Empty lines and lines beginning with `#` are ignored.
- `TypeID` is limited to 0–4.
- Names are non-empty and contain no spaces; underscores are displayed as spaces.

Malformed data causes a clear `MapDataError` instead of being silently skipped.

## Algorithm review

Dijkstra's algorithm is appropriate because negative distances are rejected. The implementation builds an undirected adjacency list, ignores stale queue entries, reconstructs the path using predecessors, and explicitly handles identical endpoints and unreachable nodes. Complexity is `O((V + E) log V)`.

The deterministic tie behavior is an implementation detail. For equal-cost paths, either valid path should be acceptable unless a tie-breaking rule is added to the specification.

## Interface review

The server returns JSON consistently:

- Success: `path` and `total_distance`.
- Bad identifiers or parameters: HTTP 400 with `error`.
- Valid but unreachable destination: HTTP 404 with `error`.
- Unauthenticated editing: HTTP 401.
- Duplicate identifiers: HTTP 409.

The browser uses these API results rather than calculating a separate answer, preventing disagreement between frontend and backend pathfinding.

## Authentication review

Authorization is enforced on the server for POST, PUT, and DELETE operations on both nodes and edges. The editor UI being hidden is only a usability measure. The shared password is read from `EDITOR_PASSWORD`; session cookies are signed by Flask's `SECRET_KEY`.

This satisfies the lab but is not production authentication. Production improvements would include individual accounts, password hashing, CSRF protection, secure-cookie configuration, rate limiting, audit logs, authorization roles, and database transactions.

## Test review

The tests assert real outputs and status codes rather than merely executing functions. Covered behaviors include path cost, identical endpoints, invalid IDs, disconnection, competing paths, file parsing, invalid references, public access, all unauthenticated editing methods, authenticated CRUD, and logout.

Remaining risks include concurrent editors, file-system failures between the two saves, extremely large graphs, browser accessibility across assistive technologies, and production security configuration.

## Cross-review comparison

The generation-oriented review was strongest at quickly proposing breadth: test maps, malformed inputs, and boundary cases. The adversarial review was stronger at questioning authorization boundaries and weak test oracles. Both could create false confidence if accepted without execution. Human review resolved ambiguous expectations and the automated suite supplied repeatable evidence.
