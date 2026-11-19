# NkwaPay loan demo: design

## Why

The group needs to show the credit scorer (`src/scorer.py`, ADR 0022) working the way a borrower would meet it: someone asks for a loan, the model scores them, and they see a decision with plain reasons. It will run live on GCP and be recorded as a start-to-finish demo video for the Prosit 2 portfolio and debrief.

## Goals
- A borrower can go from "open the link" to "loan decision" in under a minute without help.
- Every decision shown comes from the real `score()` function, unchanged.
- The look follows the Prosit 2 deck (`My Drive/MLE-GROUP-1/prosit 2/Prosit 2 Presentation.pptx`): maroon `#9D4444`, cream `#F6F2E9`, gold `#EFB05C`, sand `#E5DECF`, ink `#222222`, grey `#555555`; kente band; Adinkra symbols taken from the deck's media with the credits listed on its last slide.
- Fonts (builder's call): Poppins for headings (Google Fonts). Body uses `Candara, "Nunito Sans", system-ui` — Candara can't be served on the web, so most visitors see Nunito Sans, a close humanist match.
- A public `https://…run.app` link and a recorded video of one normal borrower's journey.

## Non-goals
- No real accounts, money, SMS, or stored applications. Nothing a borrower types is saved.
- No admin or loan-officer screens.
- No retraining; the app loads the bundle made by `python src/scorer.py --fit`.

## Anti-goals (failure even if it works)
- Looks like a generic form or a Streamlit page.
- Shows a decision the scorer didn't make, or hides that the customers are made up.
- Puts any Zindi or Findex row in the repo, the image, or the page.

## Approaches considered
- **A. FastAPI + hand-built HTML/CSS/JS in one container on Cloud Run (chosen by Joseph).** Full control of the look, one deploy, imports the tested scorer as is.
- B. Streamlit on Cloud Run: fastest, but hard to make beautiful or step-by-step.
- C. Firebase Hosting front end + Cloud Run API: two deploys and cross-site setup for no gain.

## Decided by Joseph
- **Hosting:** Cloud Run in the default project `agroconnect-highlanders`.
- **Flow:** the borrower signs in with a phone number; the app looks up a **made-up** customer record (the model's 12 history inputs come from the lender's records, as in real life), then the borrower chooses their loan.
- **Stack:** approach A on GCP Cloud Run.
- **Demo video:** recorded start to finish, showing one normal borrower.

## The flow (screens)

```
1 Welcome        NkwaPay logo · "Small loans, decided fairly"  [Get started]
                 banner: "Demo: made-up customers, no real money"
2 Phone          [ 07__ ___ ___ ]  [Continue]
                 Demo numbers: chips for each made-up customer (tap to fill)
3 Welcome back   "Welcome back, Amina" · 12 loans · 11 repaid · last loan 14 days ago  [Continue]
                 (a first-timer sees "Welcome to NkwaPay" instead)
4 Your loan      Loan type cards · Length 7 / 14 / 30 days · Amount [ 5,000 ] KES  [Check my loan]
5 Checking       short animation (~1.5 s) while the API answers
6 Decision       Approved / Starter loan / Not this time
                 Offer amount, repay amount and date · up to 3 reasons · "What you can do next"
                 ▸ How we decided — Kenya: "risk 0.8% vs our 2.1% line" (model).
                   Ghana: "this loan type's group default rate is 7.0%" + the scorer's pilot note; no cut-off shown (builder's call: the Ghana rule has no cut-off)
                 [Accept loan]  [Change my request]
7 Done           "Your loan is on its way" · amount, repay by date · [Start again]
```

Back is always possible from 3–6. Mobile-first, one column, large tap targets; works on a laptop for the recording.

## Made-up customers

Each produces the outcome shown with the current bundle (checked on 19 Nov). Phone numbers are fictional.

| Phone | Name | Country | Record | Expected with default choice |
|---|---|---|---|---|
| 0712 000 001 | Amina | Kenya | 12 loans, 11 finished, 0 missed, last 14 days ago | Approve, limit ~5,434 KES (7-day Type 1). 30 days → decline: "longer loans are repaid less often" |
| 0712 000 002 | Brian | Kenya | first loan | Starter 500 KES |
| 0712 000 003 | Wanjiru | Kenya | 3 loans, 3 missed | Decline: "You did not repay 3 of your earlier loans" |
| 0244 000 004 | Kofi | Ghana | first loan | Type 3 → starter 300 GHS; Type 2 → decline (product, not person) |

An unknown number gets "We couldn't find that number" plus the demo chips.

## Loan request → scorer
- **Loan types offered:** Kenya: Type 1 and Type 7; Ghana: Type 3 and Type 2. The data has no product names, so cards say "Type 1 · our most common loan" etc. rather than inventing meanings.
- **Lengths:** 7, 14, 30 days (95% of Kenyan loans are 7 days).
- **Amount:** the scorer gives a limit, not a yes/no on an amount. Approve: offer `min(requested, limit)`, and say so if it's lower. Starter: offer the starter amount. Decline: no offer.
- **Repay amount:** amount × (1 + fee), fee 2% Kenya / 3% Ghana (learnings/04); due date = today + length.
- The application dict is the customer's history fields + `country`, `loan_type`, `duration`, `New_versus_Repeat`; `score()` validates it as before.

## API
- `GET /api/customers/{phone}` → name, country, currency, display summary, allowed loan types. 404 if unknown. Never returns the raw model inputs.
- `POST /api/apply` `{phone, loan_type, duration, amount}` → decision, offer, repay amount, due date, reasons, notes, probability, probability source, and `cutoff` (0.021 for Kenya, `null` for Ghana). Pydantic validation; 422 on bad input.
- `GET /` serves the static page.

## Files
- `app/main.py` (FastAPI), `app/customers.py` (the four records), `app/static/` (index.html, styles.css, app.js, Adinkra SVG/PNG from the deck with credits on the page).
- `Dockerfile`, `.dockerignore`/`.gcloudignore` (send only `src/`, `app/`, `requirements` and `data/models/scorer.joblib`; never `data/zindi` or `data/worldbank`).
- `tests/test_app.py`: plain assert script like `tests/test_scorer.py`; each customer gets its expected decision; unknown phone 404; bad input 422.
- `app/demo/record.mjs`: Playwright script that walks Amina's journey on the live URL and records 1280×800 video; ffmpeg converts to MP4.

## Deploy
- **Project:** the default gcloud project, `agroconnect-highlanders` (Joseph's choice, 19 Nov). Service name `nkwapay-demo`.
- Cloud Run, region `africa-south1` (Johannesburg) if available, otherwise `europe-west1`; public (no sign-in); min instances 0, max 2.
- `gcloud run deploy --source .` builds with Cloud Build.
- The image installs the full `requirements.txt`: unpickling the bundle needs the classes in `src/amounts.py` and `src/classification_experiments.py` and their imports (scikit-learn, lightgbm, matplotlib).

## Constraints
- The joblib bundle is ignored by git (public repo) but goes into the image; it holds fitted models and a 32-value reference vector, no rows.
- The Zindi data licence covers this non-commercial course use; the page credits Zindi and says the customers are made up.
- Python 3.12 and the pinned versions in `requirements.txt`, plus `fastapi` and `uvicorn` pinned.

## Left to the builder
Exact copy, animation details, icon choices, and the video's pacing and captions.
