from typing import Annotated
import sqlite3
import pandas as pd
import os
import json
import matplotlib.pyplot as plt

from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.memory import InMemorySaver

from dotenv import load_dotenv
import logging

load_dotenv()
api_key = os.getenv("API_KEY")
logging.getLogger("langgraph").setLevel(logging.ERROR)


#Tools for agents ####################################################################33

@tool
def load_data_tool(tickers: Annotated[list[str], "List of tickers (e.g. ['AAPL', 'GOOGL])"]) -> pd.DataFrame | str:
    """
    Load 10-K concepts for one or more tickers from SQLite into a DataFrame.
    """
    db_path = os.path.join("data", "RL_database.db")
    placeholders = ",".join("?" * len(tickers))
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            f"SELECT * FROM tenk_concepts WHERE ticker IN ({placeholders})",
            conn,
            params=tickers)
    if df.empty:
        return f"No data found for: {', '.join(tickers)}."
    missing = set(tickers) - set(df['ticker'].unique())
    if missing:
        print(f"Warning: no data for {', '.join(sorted(missing))}")
    print("Successfully executed the data retrieval tool")
    return df

@tool
def compute_ratios(financials: Annotated[dict,  "Dictionary with values needed to compute ratios"]) -> dict:
    """
    Compute accounting ratios from extracted financial data.
    """
    def safe_divide(num, den):
        if den == 0:
            return None
        return num / den
    ratios = { "ticker": financials["ticker"],
            "company": financials["company"],
            "year": financials["year"],
            "profit_margin": safe_divide(financials["net_income"], financials["revenue"]),
            "roe": safe_divide(financials["net_income"], financials["all_equity_balance"]),
            "current_ratio": safe_divide(financials["current_assets_total"], financials["current_liabilities_total"]),
            "debt_to_equity": safe_divide(financials["long_term_debt"], financials["all_equity_balance"])}
    return ratios

repl = PythonREPL()
@tool
def python_repl_tool( code: Annotated[str, "The python code to execute to generate a chart."],):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user"""
    try:
        result = repl.run(code)
    except BaseException as e:
        return f"Failed to execute. Error: {repr(e)}"
    return f"Successfully executed the Python REPL tool.\n\nPython code executed:\n\`\`\`python\n{code}\n\`\`\`\n\nCode output:\n\`\`\`\n{result}\`\`\`"

# Agents #######################################################
llm = ChatOpenAI(model='gpt-4o-mini', api_key=api_key)
# Data agent
data_agent = create_react_agent( llm, tools=[load_data_tool],
    prompt=( "You are a data agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with data retrieval tasks. DO NOT write any code.\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."),
    name="data_handler") 

# Analyst agent
analytics_agent = create_react_agent( llm, tools = [compute_ratios, python_repl_tool], 
    prompt=("You are an analytics tool with two tasks: compute ratios and generate plots Python code.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist only with tasks related to compute ratios and making plots.\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Plots should be generate it and save it with plt.savefig as 'plot.png', bbox_inches='tight' and figsize=(12, 6)\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."),
    name="analytics")

config = {"configurable": {"thread_id": "1", "user_id": "1"}}
checkpointer = InMemorySaver()

#Supervisor
supervisor = create_supervisor(model=llm, agents=[data_agent, analytics_agent],
    prompt=( "You are an accounting assistant. Asnwer questions using your agents:\n"
        "- a data handler agent. Assign  data collection tasks to this agent\n"
        "- an analytics agent. Assign the creation of plots and computing ratios to this agent\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any computation or data handling yourself. Ask the agents an provide their answer"
        "You can provide finance and accounting analysis in text form'"
        "Dont answer questions unrelated to finance or accounting"),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile(checkpointer=checkpointer)

########################################
if __name__ == "__main__":
    while True:
        user_input = input("\nAsk a question, or type quit to exit: \n")
        if user_input.lower() in ("quit"):
            break

        result = supervisor.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config
        )
        print(f"\nAgent: {result['messages'][-1].content}")