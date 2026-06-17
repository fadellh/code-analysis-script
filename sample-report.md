# Commit Analysis Report

> **Note:** Generated against a public but *dormant* demo repo (`mwc-java`, last active Feb 2025), so `--days 500` was used to reach its commit history. The tool's default window is the past **7 days** (`--days 7`).

_Repo: `mwc-java` · Branch: `detailing` · Window: last 500 days (2025-02-02 → 2026-06-17) · Author: all authors_

## Summary
- **Commits analyzed:** 12 (of 17 in window) — 6 code, 6 docs
- **Total estimated effort:** 14.0 h
- **Total churn:** +1186/-117 across 54 files
- **Average quality (code only):** readability 4.5, structure 4.5, naming 4.7, error-handling 3.2, tests 2.0 → **overall 3.8/5**
- **Highlights:** highest quality `965d779` (4.4/5) · largest `9bce373` (+511/-89)

Across 6 code commits plus 6 docs commits (hours only) totaling +1186/-117 lines, estimated effort is ~14.0 h. Code quality looks solid (avg 3.8/5). Hours are size-and-complexity estimates with explicit confidence — read them as ranges, not stopwatch readings.

## Commits

### 1. `965d779` — add jacoco report
_fadellh · 2025-02-09 21:59 · +19/-0 · 1 file_

**Quality**

| Dimension | Score | Reason |
|---|---|---|
| Readability | 5/5 | clearly formatted XML with proper indentation |
| Structure | 5/5 | well-structured plugin configuration |
| Naming | 5/5 | descriptive plugin and goal names |
| Error handling | 3/5 | n/a - configuration file |
| Test coverage | 4/5 | added jacoco report configuration, but no test files touched |

**Overall quality: 4.4/5**

**Estimated hours: 0.25 h** (complexity: low, confidence: high)
> Starting from the BASELINE of 0.38 hours, we scale down due to the low complexity of the change, which is a straightforward addition of a plugin configuration. The GAP of 0.3 hours supports this estimate, as it is a relatively short time frame. Therefore, we estimate the time spent on this commit to be 0.25 hours, with high confidence.
>
> _size-only baseline: 0.38 h · prev-commit gap: 0.3 h_

### 2. `9bce373` — add unit test in order service
_fadellh · 2025-02-09 21:41 · +511/-89 · 7 files · diff truncated_

**Quality**

| Dimension | Score | Reason |
|---|---|---|
| Readability | 4/5 | added test files with clear naming, but diff is truncated and does not show the actual test code |
| Structure | 4/5 | separation of concerns is maintained with test files in separate directories, but diff does not show the actual logic changes |
| Naming | 4/5 | descriptive identifiers used in test files, such as OrderApplicationServiceTest |
| Error handling | 3/5 | n/a - test file, but actual error handling in test code is not shown in the diff |
| Test coverage | 4/5 | test files added or updated for the changed logic, such as OrderApplicationServiceTest |

**Overall quality: 3.8/5**

**Estimated hours: 3.5 h** (complexity: medium, confidence: medium)
> starting from the baseline of 4.85 hours, the complexity of the change is medium due to the addition of test files and potential logic changes. The diff is truncated and does not show the actual test code, so the estimate is based on the number of files changed and the addition of test files. The gap since the previous commit is 1.23 hours, which is a relatively short time and suggests that the commit may not represent a large amount of work. Therefore, the estimated hours are scaled down to 3.5 hours.
>
> _size-only baseline: 4.85 h · prev-commit gap: 1.23 h_

### 3. `0207aa3` — Add sonarqube
_fadellh · 2025-02-09 20:27 · +63/-10 · 8 files_

**Quality**

| Dimension | Score | Reason |
|---|---|---|
| Readability | 4/5 | clear comments and formatting in sonar-project.properties, but some files have minor formatting issues |
| Structure | 4/5 | separation of concerns in each service's BeanConfiguration, but some duplicated code across services |
| Naming | 5/5 | descriptive and consistent identifiers, such as sonar.projectKey and sonar.host.url |
| Error handling | 4/5 | added input validation in WarehouseDataAccessMapper, but no error handling in other changed files |
| Test coverage | 1/5 | no tests added or updated for the changed logic |

**Overall quality: 3.6/5**

**Estimated hours: 2.5 h** (complexity: medium, confidence: medium)
> starting from the baseline of 1.75 hours, the complexity of the changes, including the addition of SonarQube and input validation, suggests a scaling up to 2.5 hours. The GAP of 7.14 hours since the previous commit is a sanity-check upper bound, but does not directly influence the estimate. The changes are mostly boilerplate and configuration, but some novel logic is introduced, such as the input validation in WarehouseDataAccessMapper.
>
> _size-only baseline: 1.75 h · prev-commit gap: 7.14 h_

### 4. `f8f0e4e` — Update docoumentation
_fadellh · 2025-02-09 13:19 · +577/-6 · 24 files · diff truncated_

**Quality**

| Dimension | Score | Reason |
|---|---|---|
| Readability | 4/5 | clear formatting and comments in README.md |
| Structure | 4/5 | separation of concerns in documentation files |
| Naming | 5/5 | descriptive file names like aggregate-domain.png |
| Error handling | 3/5 | n/a - documentation files |
| Test coverage | 1/5 | no test files touched |

**Overall quality: 3.4/5**

**Estimated hours: 5.75 h** (complexity: low, confidence: medium)
> Starting from the baseline of 7.57 hours, we scale down due to the low complexity of the changes, which are primarily documentation updates. The large number of files changed (+577/-6 lines) is mostly due to generated documentation files. The gap since the previous commit is not directly relevant to the estimate, but it does suggest that this commit may be a batch of updates rather than a single, complex change. Overall, the estimate is adjusted downward to 5.75 hours, reflecting the relatively straightforward nature of the updates.
>
> _size-only baseline: 7.57 h · prev-commit gap: 75.76 h_

### 5. `d33fbf3` — fixing readme 📄 docs
_fadellh · 2025-02-06 09:33 · +3/-3 · 1 file_

_Documentation-only commit — code-quality scorecard n/a; hours only._

**Estimated hours: 0.25 h** (complexity: low, confidence: high)
> Starting from a BASELINE of 0.28 hours, the effort is judged to be low because the commit only involves fixing links in the README.md file, which is a routine edit. The changes are simple and do not require any dense or original technical writing. The GAP of 1.02 hours is used as a sanity-check upper bound, but the actual effort is expected to be much lower. Therefore, the estimated hours are rounded to 0.25, with high confidence.
>
> _size-only baseline: 0.28 h · prev-commit gap: 1.02 h_

### 6. `385c687` — add link to readme 📄 docs
_fadellh · 2025-02-06 08:32 · +5/-3 · 1 file_

_Documentation-only commit — code-quality scorecard n/a; hours only._

**Estimated hours: 0.25 h** (complexity: low, confidence: high)
> The commit involves adding a link to the README file, which is a simple task. The changes are minimal, with only 5 additions and 3 deletions. The BASELINE size estimate is 0.29 hours, but given the nature of the changes, the effort required is likely to be on the lower end. The GAP since the previous commit by the author is 0.32 hours, but this is not directly relevant to the effort required for this specific commit. Therefore, the estimated hours for this commit is 0.25 hours, with high confidence due to the simplicity of the task.
>
> _size-only baseline: 0.29 h · prev-commit gap: 0.32 h_

### 7. `54e2f98` — move load test result 📄 docs
_fadellh · 2025-02-06 08:13 · +3/-3 · 4 files_

_Documentation-only commit — code-quality scorecard n/a; hours only._

**Estimated hours: 0.25 h** (complexity: low, confidence: high)
> The commit involves renaming files and updating links in a README file, which is a simple and routine task. The changes are minimal and do not require any original writing or complex technical documentation. The BASELINE size estimate is 0.73 hours, but given the simplicity of the task, the actual effort required is likely to be much lower. The GAP since the previous commit is not relevant in this case, as it's not a measure of the task's complexity. Therefore, the estimated hours are rounded to 0.25, with high confidence.
>
> _size-only baseline: 0.73 h · prev-commit gap: 0.3 h_

### 8. `c0cc249` — Create CNAME
_Fadel Lukman H · 2025-02-06 08:09 · +1/-0 · 1 file_

**Quality**

| Dimension | Score | Reason |
|---|---|---|
| Readability | 5/5 | simple, one-line addition |
| Structure | 5/5 | single, focused change |
| Naming | 5/5 | clear, descriptive filename |
| Error handling | 3/5 | n/a - simple configuration file |
| Test coverage | 1/5 | no tests added or updated |

**Overall quality: 3.8/5**

**Estimated hours: 0.25 h** (complexity: low, confidence: high)
> Starting from the BASELINE of 0.26 hours, the change is a simple addition of a single line to a configuration file. Given the low complexity of the change, we scale down the estimate. The GAP of 0.08 hours is very short, but it does not affect our estimate since we are not using it as the primary factor. Therefore, we estimate the time spent on this commit to be approximately 0.25 hours.
>
> _size-only baseline: 0.26 h · prev-commit gap: 0.08 h_

### 9. `cfa0bee` — Create CNAME 📄 docs
_Fadel Lukman H · 2025-02-06 08:04 · +1/-0 · 1 file_

_Documentation-only commit — code-quality scorecard n/a; hours only._

**Estimated hours: 0.25 h** (complexity: low, confidence: high)
> The commit adds a single line to a new file, which is a simple CNAME record. The effort is minimal, as it involves creating a new file with a single line of text. The BASELINE estimate of 0.26 hours is already low, and considering the simplicity of the change, the estimated hours can be rounded down to 0.25 hours.
>
> _size-only baseline: 0.26 h · prev-commit gap: n/a_

### 10. `1c42859` — Move report to the docs
_fadellh · 2025-02-06 07:55 · +0/-0 · 3 files_

**Quality**

| Dimension | Score | Reason |
|---|---|---|
| Readability | 5/5 | no code changes, only file renames |
| Structure | 5/5 | files moved to a more appropriate location |
| Naming | 4/5 | file names are descriptive, but 'perfomace' seems to be a typo |
| Error handling | 3/5 | n/a - no code changes |
| Test coverage | 1/5 | no tests added or updated for the changed logic |

**Overall quality: 3.6/5**

**Estimated hours: 0.25 h** (complexity: low, confidence: high)
> Starting from the BASELINE of 0.55 hours, we scale down due to the simplicity of the change, which only involves renaming files. The GAP of 8.86 hours is not relevant in this case, as the change is minimal and does not require a significant amount of time. Therefore, we estimate the time spent on this commit to be around 0.25 hours.
>
> _size-only baseline: 0.55 h · prev-commit gap: 8.86 h_

### 11. `cc34ee1` — add png image 📄 docs
_fadellh · 2025-02-05 23:04 · +1/-1 · 2 files_

_Documentation-only commit — code-quality scorecard n/a; hours only._

**Estimated hours: 0.25 h** (complexity: low, confidence: high)
> The commit only involves adding a new PNG image and updating the README.md file to reference it, which is a simple and routine edit. The effort is fast since it's just a replacement of a file extension and addition of a binary file, so the estimate is rounded to the nearest 0.25 hours.
>
> _size-only baseline: 0.41 h · prev-commit gap: 0.53 h_

### 12. `2c09464` — remove markdown 📄 docs
_fadellh · 2025-02-05 22:31 · +2/-2 · 1 file_

_Documentation-only commit — code-quality scorecard n/a; hours only._

**Estimated hours: 0.25 h** (complexity: low, confidence: high)
> Starting from the BASELINE of 0.27 hours, the changes are minimal and only involve removing markdown syntax and fixing a link, which is a fast task. The changes are straightforward and do not require significant effort or complexity. Therefore, the estimated hours are rounded down to 0.25 hours with high confidence.
>
> _size-only baseline: 0.27 h · prev-commit gap: n/a_
