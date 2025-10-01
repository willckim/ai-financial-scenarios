# 📊 AI Financial Scenarios

AI-powered **Financial Scenario Generator** that lets you upload company historicals (CSV), tweak assumptions, and generate a **CFO-style forecast and analysis** using LLMs (Anthropic Claude, OpenAI GPT, or Azure OpenAI).  

Built with:
- ⚡ **FastAPI** backend (financial modeling + LLM summaries)
- 🌐 **Next.js** + **Tailwind CSS** frontend
- 🧠 Provider-agnostic LLM router (Anthropic / OpenAI / Azure)

---

## 🚀 Features
- Upload historicals (`month,revenue,cogs,opex,customers`).
- Configure assumptions:
  - Revenue growth
  - Customer churn
  - CAC / Marketing spend
  - COGS %  
  - OpEx growth
- Forecast customers, revenue, gross profit, and EBITDA.
- LLM-generated **Executive Summary** (CFO-style).
- Key metrics panel (Revenue 12m, EBITDA 12m, Margin).
- Download forecast as CSV.
- Dark glassmorphic UI inspired by **AI Research Copilot**.

---

## 🛠️ Project Structure
```text
ai-financial-scenarios/
├── server/ # FastAPI backend
│ ├── app.py # Main API (endpoints: /health, /analyze)
│ ├── finance.py # Projection logic
│ ├── llm.py # Provider-agnostic LLM wrapper
│ ├── prompts.py # System & user prompts
│ └── schemas.py # Pydantic models
│
├── frontend/ # Next.js 14 + Tailwind UI
│ ├── app/
│ │ ├── page.tsx # Root page -> Fin Scenarios
│ │ └── fin-scenarios/ # Main feature UI
│ └── globals.css # Tailwind setup
│
├── sample_data/
│ └── historicals_example.csv # Example input
│
└── README.md
```
## ⚙️ Setup

### 1. Backend (FastAPI)
```bash
cd server
python -m venv .venv
.venv\Scripts\activate  # (Windows PowerShell)
pip install -r requirements.txt

# Run locally
uvicorn server.app:app --reload --port 8000
```

Check it’s live:

http://127.0.0.1:8000/health

### 2. Frontend (Next.js + Tailwind)
```bash
cd frontend
npm install

# Dev server
npm run dev
```

Runs at:

http://localhost:3000


Frontend talks to backend via:

NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000


(add this in frontend/.env.local)

## 📂 Example Workflow

Run backend (uvicorn …).

Run frontend (npm run dev).

Open http://localhost:3000.

Upload sample_data/historicals_example.csv.

Adjust assumptions → Run Scenario.

View forecast + CFO analysis + export CSV.

## 🌐 Deployment

Backend → Render / GCP Cloud Run

Frontend → Vercel

Set env vars in hosting platform:
```bash
NEXT_PUBLIC_BACKEND_URL=https://your-backend-url.com
```

## 📜 License

MIT — free to use, and share.

## ✨ Credits

Built by William Kim

---