# 📊 RatioLens

An AI-powered financial analysis chatbot that lets you query SEC EDGAR 10-K data, compute accounting ratios, and generate charts — all through a conversational interface.

---

## What it does

- **Natural language queries** — ask questions like "Compare MSFT vs GOOGL margins" or "Net income of AAPL"
- **Loads 10-K financial data** from a local SQLite database (populated from SEC EDGAR)
- **Computes accounting ratios** — profit margin, ROE, current ratio, debt-to-equity
- **Generates charts** via a Python REPL agent and displays them inline in the chat
- **Multi-agent architecture** — a supervisor delegates to a data agent and an analytics agent

---

## Architecture

```
User → Streamlit UI
         └── Supervisor (GPT-4o-mini)
               ├── Data Agent  →  load_data_tool  →  SQLite (RL_database.db)
               │                                          └── tenk_concepts
               └── Analytics Agent  →  compute_ratios
                                    →  python_repl_tool  →  plot.png
```

The supervisor uses LangGraph with `InMemorySaver` for conversation memory across a session. Agents are called sequentially (not in parallel).

---

## Project structure

```
RatioLens/
├── RatioLens_UI.py          # Streamlit chat interface
├── agentic_functions.py     # LangGraph agents, tools, and supervisor
├── sqlite_code.py           # Database setup and record management
├── data/
│   └── RL_database.db       # SQLite database with 10-K concepts
└── .env                     # API key (not committed)
```

---

## Setup

### 1. Install dependencies

```bash
pip install streamlit langchain langchain-openai langchain-experimental langgraph langgraph-supervisor python-dotenv pandas matplotlib
```

### 2. Configure your API key

Create a `.env` file in the project root:

```
API_KEY=your_openai_api_key
```

### 3. Initialize the database

```bash
python sqlite_code.py
```

This creates `data/RL_database.db` with the `tenk_concepts` and `accounting_ratios` tables.

### 3. Populate the database

```bash
python get_sec_edgar_data.py
```

This creates `data/RL_database.db` with the `tenk_concepts` and `accounting_ratios` tables.

### 5. Run the app

```bash
streamlit run RatioLens_UI.py
```

---

## Supported tickers

Includes 35+ tickers across big tech, semiconductors, fintech, cloud, and consumer tech:

`AAPL` `MSFT` `GOOGL` `META` `AMZN` `NVDA` `TSLA` `V` `MA` `SNOW` `PLTR` and more.

---


## Database schema

**`tenk_concepts`** — raw 10-K financials per ticker per year:

| Column | Type |
|---|---|
| ticker | TEXT |
| company | TEXT |
| year | TEXT |
| revenue | REAL |
| gross_profit | REAL |
| net_income | REAL |
| current_assets_total | REAL |
| assets | REAL |
| current_liabilities_total | REAL |
| long_term_debt | REAL |
| all_equity_balance | REAL |

---

## Example prompts

- `Net income of AAPL`
- `Compare MSFT vs GOOGL profit margins`
- `Plot revenue trend for NVDA`
- `Debt-to-equity ratio for META and AMZN`
