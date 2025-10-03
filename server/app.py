from __future__ import annotations
import os, io
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from dotenv import load_dotenv

# Load env that sits next to this file (server/.env)
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

# ---- make imports work whether run as `server.app` or `app` ----
try:
    # when run as a package from repo root: `uvicorn server.app:app`
    from .schemas import Scenario, AnalyzeResponse
    from .finance import project
    from .prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
    from .llm import LLM
except ImportError:  # when run from inside server/: `uvicorn app:app`
    from schemas import Scenario, AnalyzeResponse
    from finance import project
    from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
    from llm import LLM
# ---------------------------------------------------------------

app = FastAPI(title="Financial Scenario Generator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your domains for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = LLM()

@app.get("/health")
def health():
    return {
        "ok": True,
        "providers": {
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "azure": bool(os.getenv("AZURE_OPENAI_ENDPOINT") and os.getenv("AZURE_OPENAI_API_KEY")),
        },
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: UploadFile = File(...),
    scenario_json: str = Form('{"months_ahead":12}'),
    provider: str = Form("anthropic"),
    model: str = Form(""),
    max_gen_tokens: int = Form(2200),
):
    try:
        scenario = Scenario.model_validate_json(scenario_json)
    except ValidationError as e:
        return {"forecast": [], "summary": f"Invalid scenario: {e}", "key_metrics": {}}

    content = await file.read()
    try:
        hist = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {e}")

    required = {"month", "revenue", "cogs", "opex", "customers"}
    cols_lower = [c.lower() for c in hist.columns]
    missing = required - set(cols_lower)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {sorted(missing)}")

    hist.columns = cols_lower
    proj = project(hist, scenario.months_ahead, scenario.model_dump(exclude_none=True))

    rev_total = float(proj["revenue"].sum())
    ebitda_total = float(proj["ebitda"].sum())
    end_margin = float(proj["ebitda_margin"].iloc[-1])

    hist_small = hist.tail(6).to_string(index=False)
    proj_small = proj.head(min(6, len(proj))).to_string(index=False)
    user_prompt = USER_PROMPT_TEMPLATE.format(
        historicals_table=hist_small,
        months=scenario.months_ahead,
        projection_table=proj_small,
        assumptions=scenario.model_dump(exclude_none=True),
    )

    try:
        summary_text = llm.generate(
            provider=(provider or "anthropic"),
            system=SYSTEM_PROMPT,
            user=user_prompt,
            model=(model or None),
            max_tokens=max_gen_tokens,
            temperature=0.2,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    return AnalyzeResponse(
        forecast=proj.to_dict(orient="records"),
        summary=summary_text,
        key_metrics={
            "revenue_12m": round(rev_total, 2),
            "ebitda_12m": round(ebitda_total, 2),
            "ebitda_margin_last": round(end_margin, 4),
        },
    )
