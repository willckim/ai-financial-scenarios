SYSTEM_PROMPT = """You are a CFO-level analyst.
Explain financial projections clearly and conservatively.
When citing numbers, use those provided in the JSON tables.
Provide: 1) executive summary, 2) key drivers, 3) risks & mitigations,
4) sensitivity notes (what changes matter most). Keep it concise."""

USER_PROMPT_TEMPLATE = """Historicals + Projection:

- Trailing historical monthly data (USD):
{historicals_table}

- Forward projection (next {months} months):
{projection_table}

Assumptions:
{assumptions}

Tasks:
1) Summarize revenue, gross profit, EBITDA trend.
2) Call out inflection points (month over month).
3) Identify top 2–3 levers (price, churn, CAC, marketing spend, COGS%, opex growth).
4) List 3 risks with mitigations.
5) Give a 2–3 sentence 'Board-ready' summary."""
