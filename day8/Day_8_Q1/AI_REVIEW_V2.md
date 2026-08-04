# Question 1 — V2 AI Review Record

## Activity 1: AI-generated test expansion

### Prompt

> Review this C++ command-line multiplication program and propose additional test cases. Include zero position, multiplication by one, mixed signs, and larger values. For every case, state the inputs, expected output, and rationale. Keep values within a C++ 32-bit signed integer because the starter uses `int`.

### Reviewed suggestions

| Inputs | Expected | Rationale | Decision |
|---|---:|---|---|
| `7, 0` | `0` | Checks zero as the second operand | Accepted |
| `123, 1` | `123` | Checks the multiplicative identity | Accepted |
| `5, -6` | `-30` | Checks positive-by-negative sign handling | Accepted |
| `1000, 1000` | `1000000` | Checks a larger, valid result | Accepted |
| `50000, 50000` | `2500000000` | Challenges 32-bit range | Rejected as a normal passing case because signed `int` overflow is outside the starter's defined behavior |
| `hello, 4` | input error | Challenges parsing | Recorded as a design weakness; not added to the tuple harness because `atoi` currently accepts invalid text as zero |

The four accepted cases were added to `python/check_multiply.py`, giving eight result-based cases in total.

## Activity 2: Sanitized Jenkins failure diagnosis

The log excerpt supplied for review omitted the Jenkins username and unrelated environment details:

```text
3 * 4 = 7
FAILED
0 * 0 = 0
-3 * 4 = 1
FAILED
-3 * -4 = -7
FAILED
TEST FAILURE
ERROR: script returned exit code 1
Finished: FAILURE
```

### Diagnosis prompt

> Given this sanitized Jenkins failure output and the intended multiplication behavior, identify the root cause, propose the minimal fix, explain why the Python smoke test can still pass, and suggest a regression test.

### Diagnosis and human assessment

The results match addition rather than multiplication: `3 + 4 = 7`, `-3 + 4 = 1`, and `-3 + -4 = -7`. The minimal fix is to restore `a * b` in `cpp/multiply.cpp`. The smoke test only checks Python's `1 + 1 == 2`, so it proves pytest runs but does not exercise the C++ program. The existing `3, 4 → 12` integration case is already a regression test; retaining the four new cases makes accidental operator substitution even more visible. This diagnosis agrees with the code change and executable evidence.

## Activity 3: Different-prompt code and test review

### Prompt

> Act as a strict software reviewer. Review `multiply.cpp` and `python/check_multiply.py` separately for correctness, edge cases, invalid input, overflow, test-oracle quality, style, and maintainability. Do not assume passing tests prove completeness.

### Findings

- `argc != 3` is handled clearly.
- `atoi` silently converts invalid input to zero, so malformed input is not rejected reliably.
- Signed `int` multiplication can overflow; reviewed passing cases therefore stay within range.
- The Python script has explicit expected outputs and exits non-zero on mismatches, making Jenkins failures meaningful.
- The four added cases improve zero-position, identity, sign, and larger-value coverage.
- The smoke test is infrastructure evidence, not multiplication evidence.
- A production version should use checked parsing, define a numeric range, and test rejected inputs and overflow.

## Comparison of AI findings and Jenkins evidence

The test-generation prompt was best for producing candidate inputs quickly. The strict review found deeper specification gaps around parsing and overflow. The failure-diagnosis prompt correctly inferred the operator defect from outputs, but that inference alone was not proof. Jenkins recompiled the saved source and executed expected-output checks, providing repeatable evidence that the defect changed observable behavior.

AI review identified possibilities and review questions. Jenkins proved only that the configured cases passed or failed; it did not prove correctness for every integer, invalid input, security property, or unstated requirement. Human judgement was needed to reject an overflowing case, accept cases with reliable expected outputs, restore the intended operator, and decide what the lab-grade program promises.

## Final restoration

The submitted source contains the correct expression `a * b`. After adding the four reviewed cases, Jenkins must be run one final time and its `ALL TESTS PASSED` / `Finished: SUCCESS` evidence attached. V2 requires this real final execution.
