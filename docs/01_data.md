# 01 · Data: where it came from and what we found

```
data/                       # never committed
  zindi/       Train.csv  Test.csv  SampleSubmission.csv  economic_indicators.csv  VariableDefinitions.txt
  worldbank/   micro_gha.csv
```

## African Credit Scoring Challenge (Zindi)

**What it is:** loan-level records. Train.csv has Kenyan loans with a default label; Test.csv has unlabelled Kenyan and Ghanaian loans; economic_indicators.csv has FRED macro data per country and year.

**How we got it:**
1. Went to <https://zindi.africa/competitions/african-credit-scoring-challenge> (now redirects to zindi.world).
2. Logged in with a free account and joined the competition, accepting its rules.
3. **Data** tab → downloaded all files → put them in `data/zindi/`.

**Licence terms that affect us:**
- *"The data is private property of the client."* We never commit it or share the raw files outside the group, and we don't upload raw rows to AI tools.
- Only open-source tools are allowed.

**Submissions:** the competition closed on 12 Jan 2025, but the **Get a score** button still works, with 10 submissions per day. A score covers Kenya and Ghana test rows together, so it can't isolate how we do on Ghana. Germain logs every submission and its score in `02_classification`.

### The columns (from VariableDefinitions.txt)

`ID`, `customer_id`, `country_id`, `tbl_loan_id`, `lender_id`, `loan_type`, `Total_Amount`, `Total_Amount_to_Repay`, `disbursement_date`, `due_date`, `duration`, `New_versus_Repeat`, `Amount_Funded_By_Lender`, `Lender_portion_Funded`, `Lender_portion_to_be_repaid`, `target` (1 = defaulted).

**The brief's names don't match the data:** it mentions `ProductCategory` and `IsDefaulted`, which don't exist. The real columns are `loan_type` and `target`.

### Zindi checks

| Check | Brief says | Data has |
|---|---|---|
| Train rows / defaults | 68,654 / 1,258 (1.83%) | 68,654 / 1,258 (1.83%) ✅ |
| Train countries | Kenya | Kenya only ✅ |
| Test rows | 18,594, ~81% Kenya / ~19% Ghana | 18,594, 81% / 19% ✅ |
| Customers in both files | ~4,306 | 4,306 ✅ |
| Loan IDs in both files | ~920 | 920 ✅ |
| Missing values | — | none |
| Disbursement dates | — | Train Oct 2021 – Nov 2024; Test Nov 2021 – Nov 2024 |

How we checked (run from the repo root):

```sh
.venv/bin/python -I - data/zindi <<'EOF'
import sys, pandas as pd
d = sys.argv[1]
tr = pd.read_csv(f'{d}/Train.csv'); te = pd.read_csv(f'{d}/Test.csv')
print('train', tr.shape, 'defaults', tr.target.sum(), round(tr.target.mean()*100, 2), '%')
print('test', te.shape, te.country_id.value_counts(normalize=True).round(3).to_dict())
print('customer overlap', len(set(tr.customer_id) & set(te.customer_id)))
print('loan_id overlap', len(set(tr.tbl_loan_id) & set(te.tbl_loan_id)))
print('missing', tr.isna().sum().sum())
EOF
```

### What the checks found

1. **The 920 shared loan IDs are not duplicates.** For every pair, the customer and disbursement date are the same but the **lender is different**. Zindi's notes say "a loan can have multiple lender IDs", so these are different lenders' shares of one loan.
   - When building borrower history, rows with the same loan ID must **not** count as each other's "past loans".
   - Grouping folds by customer keeps them together automatically.
2. **Ghana and Kenya amounts aren't comparable as they stand.** This assumes amounts are in local currency; the files don't say.
   - Ghana's median `Total_Amount` is 3,002, about **$270** at the 2023 rate of 11.0 GHS per USD.
   - Kenya's is 5,249, about **$38** at 139.8 KES per USD.
   - So Ghanaian loans look about **7× bigger** in dollars. Converting to USD is a must-test scenario for the transfer study.
3. **Ghana's product mix is different:** 3 loan types and 5 lenders, against 22 loan types and 4 lenders for Kenya (train and test combined). Median duration is 7 days in both.
4. **The macro data stops at 2023, but loans run to Nov 2024.** We need a rule for 2024 (e.g. carry 2023 forward) and will test it against alternatives. The file is "wide": one column per year (`YR2001`–`YR2023`), one row per country × indicator, and it also includes Côte d'Ivoire, which we drop. It must be reshaped to one row per country-year before joining.
5. **Only 736 of 87,248 loans (0.8%) are "New".** The thin-file fairness comparison rests on a small group, so its confidence intervals will be wide. The report must say so.

## Global Findex Ghana 2021 (World Bank)

**What it is:** a survey of 1,000 Ghanaian adults covering bank and mobile-money accounts, borrowing and saving. We use it to describe who in Ghana lacks access to credit (Part D4). It is also our only source for gender, which the loan data doesn't have.

**How we got it:**
1. Went to <https://microdata.worldbank.org/index.php/catalog/4646> → **Get Microdata**.
2. Registered for a free account and accepted the terms.
3. Filled in the "intended use" form with:

   > **Project question:** How can a digital lender in Ghana make fair, transparent credit decisions that widen access to credit instead of narrowing it? This is group coursework for ICS553 Machine Learning Essentials (MSc Intelligent Computing Systems, Ashesi University, Ghana).
   >
   > **Objectives:** We are building a credit-scoring model for small mobile-money loans and auditing it for fairness. We will use the Global Findex Ghana 2021 data to describe who currently lacks access to credit in Ghana (by gender, region, income, education and rural/urban residence), and to judge whether our model would narrow or widen those gaps.
   >
   > **Methods:** Weighted descriptive statistics and cross-tabulations of account ownership, mobile money use, borrowing and saving, using the survey weights. All analysis is at the aggregate level. We will not try to identify respondents, and we will not link the data to any other individual-level dataset.
   >
   > **Expected outputs:** Aggregated tables and charts in a course technical report and an in-class presentation, citing the dataset. The microdata will not be redistributed.
   >
   > **Partners:** None. This is academic coursework supervised by the course lecturer at Ashesi University.

4. Downloaded the CSV → `data/worldbank/micro_gha.csv`.

**Licence terms that affect us:**
- **"Used solely by the user", with no redistribution.** Anyone else who analyses it (Liza) registers for their own copy instead of being sent this file.
- **Aggregate reporting only**, and no attempts to identify respondents.
- **No linking to other datasets in ways that could identify people.** We only compare aggregates with the Zindi data, never row by row.
- We must **cite the dataset** (DOI <https://doi.org/10.48529/gs06-7r65>).

### Findex checks

| Check | Result |
|---|---|
| Rows / columns | 1,000 respondents / 120 columns ✅ (brief says n = 1,000) |
| Country | Ghana only |
| Useful columns | `wgt` (survey weight), `female`, `age`, `educ`, `inc_q` (income quintile), `emp_in`, `urbanicity_f2f`, `account`, `account_mob`, `borrowed`, `saved`, `fin22a/b/c` (borrowing sources), `mobileowner` |
| Region | **Not in the file.** The brief asks for "gender and region inclusion", but only urban/rural is available. The report must say region can't be analysed with this file. |

**Before analysing it:**
- **The answers are numeric codes**, e.g. `female` 1/2 and `educ` 1/2/3/5. We need the questionnaire or codebook from the catalog page's **Documentation** tab to know what each code means. *(Still to get.)*
- **Every percentage must use the survey weight `wgt`.** Unweighted counts misrepresent Ghana's population.
