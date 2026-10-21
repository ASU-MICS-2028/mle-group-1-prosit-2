# Log

Newest at the bottom. One line per action: date · who · what · where.

| Date | Who | What | Where |
|---|---|---|---|
| 16 Oct 2026 | — | Prosit 2 launched (brief: *Prosit 2 - ICS553 MLE.pdf*) | Course page |
| 18 Oct 2026 | Joseph | Read the brief; drafted the full plan, roles and timeline | [00_project_setup.md](00_project_setup.md) |
| 18 Oct 2026 | Joseph | Created the GitHub repo structure: README, pinned `requirements.txt`, `.gitignore` (keeps `data/` out), four notebook skeletons with owner and team rules; checked all four run | commit `Project repository set up` |
| 18 Oct 2026 | Joseph | Checked Zindi: competition closed 12 Jan 2025; page didn't say whether late submissions are scored | [01_data.md](01_data.md) |
| 18 Oct 2026 | Joseph | Put the plan in Google Drive (`MLE-GROUP-1 / prosit 2 / MLE-GROUP-1-PROSIT-2 Plan`) for everyone to review and sign off | [Plan doc](https://docs.google.com/document/d/16AOzssRkISRfICwckw1Q6OZXXJYGGTe4fnw9fxffBx0/edit) |
| 18 Oct 2026 | Joseph | Shared the plan doc with the group | Google Drive |
| 20 Oct 2026 | Joseph | Mapped which parts depend on which; added the step table to the README | [00_project_setup.md](00_project_setup.md#who-waits-on-whom), README |
| 20 Oct 2026 | Joseph | Downloaded the Zindi data to `data/zindi/`; checked it against the brief (all numbers match) | [01_data.md](01_data.md#zindi-checks) |
| 20 Oct 2026 | Joseph | Found the 920 shared loan IDs are one loan split across lenders, not duplicates; Ghana amounts ~7× Kenya in USD; macro data stops at 2023; only 736 "New" loans | [01_data.md](01_data.md#what-the-checks-found) |
| 20 Oct 2026 | Joseph | Confirmed Zindi still scores late submissions (10/day); added step 7b (Germain) | README |
| 20 Oct 2026 | Joseph | Registered with the World Bank Microdata Library; downloaded Findex Ghana 2021 to `data/worldbank/micro_gha.csv`; checked it | [01_data.md](01_data.md#findex-ghana-2021) |
| 20 Oct 2026 | Joseph | Created this `docs/` folder and wrote up everything above | `docs/` |
| 20 Oct 2026 | Joseph | Handed the feature audit (step 3) fully to Liza; wrote the step-by-step guide in the README; created `notebooks/00_feature_audit.ipynb`; moved its due date to Wed 21 Oct | README § Step 3 |
| 20 Oct 2026 | Joseph | Added `knowledge/`: the brief and syllabus essentials as markdown, plain-language lecture notes, derivations, book chapter map, regulation (BoG Directive, Acts 843 and 726) and fairness-reading notes, and summaries of the lecture recordings. No original course files committed (repo is public). Written with AI assistance (see AI declaration). | [knowledge/README.md](../knowledge/README.md) |
| 20 Oct 2026 | Joseph | Added `learnings/` and team rule 4: each member fully explains their step there, in the simplest language possible, so others can understand without rerunning anything. Feature audit write-up moved there. | [learnings/README.md](../learnings/README.md) |
| 20 Oct 2026 | Liza | Feature audit (step 3): timeline, label definition, four leakage tests, feature-set comparison; found `Total_Amount_to_Repay` leaks post-default penalties (PR-AUC 0.20 → 0.91 with leaks); froze features as `loan_type`, `duration`, `New_versus_Repeat`, calendar parts of `disbursement_date` | [learnings/03_feature_audit.md](../learnings/03_feature_audit.md), `notebooks/00_feature_audit.ipynb` |
| 20 Oct 2026 | Liza | Installed `libomp` (Homebrew) so LightGBM runs on macOS; added it to the README setup | README |
| 21 Oct 2026 | Liza | Cost matrix (step 4): typical loan, fees from repaid loans, cost of FN 4,700 KES / 2,716 GHS vs FP 100 KES / 90 GHS → decline above 2.1% (Kenya) / 3.2% (Ghana); sensitivity: 1.9–2.6% / 2.9–4.1% for recovery and collection guesses, 9.6% / 14.2% with lost repeat business | [learnings/04_cost_matrix.md](../learnings/04_cost_matrix.md), `notebooks/00b_cost_matrix.ipynb` |
