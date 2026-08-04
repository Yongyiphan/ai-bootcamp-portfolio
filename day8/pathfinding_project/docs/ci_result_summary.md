# CI Result Summary — Day 8 Lab V2

## Question 1 evidence captured

### Initial successful pipeline

- Jenkins build: **#1**
- Result: **SUCCESS**
- Screenshot: `docs/screenshots/jenkins-success.png`
- Console log: `docs/evidence/question1-jenkins-success.txt`
- Evidence: pytest passed, C++ compiled with warnings, four starter integration cases passed, and Jenkins reported `Finished: SUCCESS`.

### Intentional regression

- Jenkins build: **#2**
- Result: **FAILURE**
- Screenshot: `docs/screenshots/jenkins-fail.png`
- Console log: `docs/evidence/question1-jenkins-intentional-failure.txt`
- Evidence: replacing multiplication with addition produced `7`, `1`, and `-7`; the verifier exited with status 1 and Jenkins reported `Finished: FAILURE`.

### V2 final restored build

The multiplication source is restored and four reviewed cases have been added. V2 requires another real Jenkins run after both changes.

- Build number: **pending final run**
- Expected result: **SUCCESS**
- Required screenshot: `docs/screenshots/question1-final-success-v2.png`
- Required log: `docs/evidence/question1-final-success-v2.txt`
- Required console evidence: all eight cases, `ALL TESTS PASSED`, and `Finished: SUCCESS`.

Do not reuse build #1 here: it ran before the four V2 test additions.

### V2 direct Docker verification

- Result: **PASS**
- Evidence: `docs/evidence/question1-docker-v2.txt`
- `/app/multiply 3 4` returned `12`.
- The in-container verifier ran all eight cases and printed `ALL TESTS PASSED`.

## Question 2 local verification

- Date: 22 July 2026
- Command: `python -m pytest -q`
- Result: **16 passed**

Add actual Question 2 Jenkins information here if it is run through Jenkins.

## Evidence integrity

Screenshots and logs must come from actual execution. Remove or hide credentials, tokens, passwords, personal data, and unrelated environment details before sharing console excerpts with an AI service.
