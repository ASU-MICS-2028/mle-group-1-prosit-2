"""Loan demo: a borrower signs in with a phone number, asks for a loan, and gets the scorer's decision (ADR 0022). Run: uvicorn app.main:app"""
from contextlib import asynccontextmanager
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.customers import CUSTOMERS, normalise_phone
from src.scorer import KENYA_CUT, load, score

STATIC = Path(__file__).parent / "static"
FEE = {"Kenya": 0.02, "Ghana": 0.03}  # learnings/04_cost_matrix.md


@asynccontextmanager
async def lifespan(_):
    load()  # fail at start-up, not on the first borrower, if the bundle is missing
    yield

app = FastAPI(title="NkwaPay loan demo", lifespan=lifespan, docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def customer(phone: str) -> dict:
    c = CUSTOMERS.get(normalise_phone(phone))
    if c is None: raise HTTPException(404, "not found")
    return c


class Application(BaseModel):
    phone: str = Field(max_length=32)
    loan_type: str = Field(max_length=16)
    duration: Literal[7, 14, 30]
    amount: float = Field(ge=1, le=1_000_000)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/customers/{phone}")
def get_customer(phone: str):
    c = customer(phone)
    return dict(phone=normalise_phone(phone), name=c["name"], country=c["country"], currency=c["currency"],
                summary=c["summary"], loan_types=c["loan_types"], first_loan=c["history"]["n_prev_loans"] == 0)


@app.post("/api/apply")
def apply(a: Application):
    c = customer(a.phone)
    if a.loan_type not in {t["code"] for t in c["loan_types"]}: raise HTTPException(422, "loan type not offered here")
    r = score({**c["history"], "country": c["country"], "loan_type": a.loan_type, "duration": a.duration})
    offer = min(round(a.amount), r["limit"]) if r["decision"] in ("approve", "starter") else 0  # never more than was asked for
    return dict(decision=r["decision"], offer=offer, requested=round(a.amount), limit=r["limit"], currency=r["currency"],
                repay=round(offer * (1 + FEE[c["country"]])), due_date=(date.today() + timedelta(a.duration)).isoformat(),
                reasons=r["reasons"], notes=r["notes"], probability=r["probability"], probability_source=r["probability_source"],
                cutoff=KENYA_CUT if c["country"] == "Kenya" else None)
