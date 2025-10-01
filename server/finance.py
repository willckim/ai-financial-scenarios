from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, Any

def trailing_growth(series: pd.Series, months: int = 3) -> float:
    """Simple trailing CAGR-ish monthly growth estimate."""
    s = series.dropna()
    if len(s) < months + 1:
        return 0.01
    start = s.iloc[-months-1]
    end = s.iloc[-1]
    if start <= 0:
        return 0.01
    return (end / start) ** (1 / months) - 1

def project(
    hist: pd.DataFrame,
    months_ahead: int,
    assumptions: Dict[str, Any]
) -> pd.DataFrame:
    """
    Build a light 12M model:
      - Revenue = customers * price
      - Customers evolve with churn & new_acq (marketing_spend / CAC)
      - COGS% and Opex grow with opex_growth_m
    """
    df = hist.copy()
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values("month").reset_index(drop=True)

    # Defaults + fallbacks from trailing data
    rev_growth_m = assumptions.get("rev_growth_m", trailing_growth(df["revenue"]))
    churn_m = assumptions.get("churn_m", 0.02)
    cac = assumptions.get("cac", 120.0)
    marketing_spend = assumptions.get("marketing_spend", 3000.0)
    price = assumptions.get("price", max(1.0, (df["revenue"].iloc[-1] / max(df["customers"].iloc[-1], 1))))
    cogs_pct = assumptions.get("cogs_pct", float(df["cogs"].iloc[-1] / max(df["revenue"].iloc[-1], 1)))
    opex_growth_m = assumptions.get("opex_growth_m", 0.01)

    last_month = df["month"].iloc[-1]
    customers = float(df["customers"].iloc[-1])
    opex = float(df["opex"].iloc[-1])

    rows = []
    for i in range(1, months_ahead + 1):
        month = (last_month + pd.offsets.DateOffset(months=i)).to_period("M").to_timestamp()

        # customer evolution
        churned = customers * churn_m
        new_acq = marketing_spend / max(cac, 1e-6)
        customers = max(0.0, customers - churned + new_acq)

        # price-driven revenue with optional top-line growth overlay
        price *= (1 + rev_growth_m)
        revenue = customers * price

        cogs = revenue * cogs_pct
        opex = opex * (1 + opex_growth_m)

        gross_profit = revenue - cogs
        ebitda = gross_profit - opex
        margin = ebitda / revenue if revenue else 0.0

        rows.append({
            "month": month.strftime("%Y-%m"),
            "customers": round(customers, 2),
            "price": round(price, 2),
            "revenue": round(revenue, 2),
            "cogs": round(cogs, 2),
            "opex": round(opex, 2),
            "gross_profit": round(gross_profit, 2),
            "ebitda": round(ebitda, 2),
            "ebitda_margin": round(margin, 4),
            "churned": round(churned, 2),
            "new_acq": round(new_acq, 2)
        })

    proj = pd.DataFrame(rows)
    return proj
