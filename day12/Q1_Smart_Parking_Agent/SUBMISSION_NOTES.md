# Day 12 Q1 Submission Notes

## Verification

- Guided tests: 5/5 passed.
- Student tests: 21/21 passed.
- Final controller status: `PASSED -- all_tests_passed`.
- Web/API demonstrations verified: `PAY`, `CREDIT`, and rejected V2G export below minimum departure SOC.

## Evidence Questions

1. **Which observation caused each repair?**
   The starter candidate compiled but failed all five guided tests, so the controller selected `REPAIR`. Candidate 1 passed four of five tests but failed the minimum-departure-SOC case, so the controller selected `REPAIR` again. Candidate 2 passed all selected tests and was accepted.

2. **What defect remained in candidate 1?**
   Candidate 1 checked the vehicle type, V2G capabilities, and owner consent, but did not reject an export when `soc_after_export` was below `minimum_departure_soc`.

3. **Which independent conditions prevent an endless loop?**
   The maximum-iteration budget bounds repair attempts. Repeated candidate hashes and repeated failure signatures independently detect non-progress and cause escalation.

4. **Why is a candidate hash different from a failure signature?**
   The candidate hash identifies the exact source text. The failure signature identifies the observed set of failing tests and reasons. Different source files can produce the same failure signature, while the same source always produces the same candidate hash.

5. **What could still be wrong after the visible tests pass?**
   Untested boundaries, misunderstood requirements, integer-range assumptions, platform differences, and production concerns such as authenticated identities, trusted meters, tariff versions, consent evidence, transaction controls, and deployment approval may remain. Passing visible tests is evidence, not proof of complete correctness.
