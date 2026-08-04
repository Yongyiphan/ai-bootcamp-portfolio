# Verification Test Plan

| ID | Input or action | Expected result | Automated evidence |
|---|---|---|---|
| P01 | Path 0 → 2 | `0 → 1 → 2`, distance 230 | `test_public_can_view_map_and_find_path` |
| P02 | Start equals end | One-node path, distance 0 | `test_start_equals_end` |
| P03 | Invalid start 99 | Clear invalid-start error | `test_invalid_nodes` |
| P04 | Invalid end 99 | Clear invalid-end error | `test_invalid_nodes` |
| P05 | Path to isolated node | No-path result / HTTP 404 | `test_unreachable_destination`, web test |
| P06 | Direct expensive edge vs multi-edge route | Lower total cost selected | `test_normal_shortest_path_uses_edge_distance` |
| P07 | Comments and blank records | Ignored during loading | `test_loader_ignores_comments_and_blank_lines` |
| P08 | Edge references unknown node | Map rejected | `test_loader_rejects_unknown_edge_node` |
| P09 | Duplicate node ID | Map rejected | `test_loader_rejects_duplicate_node_id` |
| A01 | Public map and path GET | HTTP 200 without login | `test_public_can_view_map_and_find_path` |
| A02 | Six public mutation requests | Every request returns HTTP 401 | `test_every_edit_method_rejects_public_user` |
| A03 | Incorrect editor password | HTTP 401 | `test_failed_login` |
| A04 | Authenticated node CRUD | Add, update, delete succeed and persist | editor node CRUD test |
| A05 | Authenticated edge CRUD | Add, update, delete succeed and persist | editor edge CRUD test |
| A06 | Logout followed by edit | Edit returns HTTP 401 | `test_logout_removes_editor_access` |

## Actual result

Local run on 22 July 2026:

```text
................                                                         [100%]
16 passed in 0.28s
```

Result: **PASS**.
