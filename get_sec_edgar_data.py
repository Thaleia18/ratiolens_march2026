from sqlite_code import *
import sqlite3
import requests
import pandas as pd
import time
from edgar import *
import json
import os

def get_from_income_statement(income_statement_xbrl, year): 
    """
    Extract income statement concepts for a given fiscal year from XBRL data.
    Args:
        income_statement_xbrl: XBRL income statement object 
        year: Fiscal year as a string (e.g. "2023").
    Returns:
        List of [year, concept_name, value] triples with concepts 'revenue', 'netincome', 'grossprofit'.
        Returns an empty list if no matching concepts are found.
    """
    info = []  
    income_statement_concepts = ['revenue', 'netincome', 'grossprofit']
    if income_statement_xbrl is None:
        return []
    df = income_statement_xbrl.to_dataframe()
    data = json.loads(df.to_json(orient="records"))
    for element in data:
        sc = element.get('standard_concept')
        if not sc or sc == 'None':
            continue
        if sc.lower() in income_statement_concepts:
            values = [v for k, v in element.items() if k.startswith(year)]
            if len(values)>0:
                info.append([year, sc.lower(), float(values[-1])])
    return info

def get_from_balance_sheet(balance_sheet_xrbl, year):
    """
    Extract balance sheett concepts for a given fiscal year from XBRL data.
    Args:
        balance_scheet_xbrl: XBRL income statement object 
        year: Fiscal year as a string (e.g. "2023").
    Returns:
        List of [year, concept_name, value] triples with concepts 'currentassetstotal', 'currentliabilitiestotal', 'assets', 'longtermdebt', 'allequitybalance'.
        Returns an empty list if no matching concepts are found.
    """
    bs_concepts = ['currentassetstotal', 'currentliabilitiestotal', 'assets', 'longtermdebt', 'allequitybalance']
    info = []
    if balance_sheet_xrbl is None:
        return []
    df = balance_sheet_xrbl.to_dataframe()
    data = json.loads(df.to_json(orient="records"))
    for element in data:
        sc = element.get('standard_concept')
        if not sc or sc == 'None':
            continue
        if sc.lower() in bs_concepts:
            values = [v for k, v in element.items() if k.startswith(year)]
            if len(values)>0:
                info.append([year, sc.lower(), float(values[-1])])
    return info

def get_concepts(ticker, year):
    """
    Fetch and extract financial concepts for a given ticker and fiscal year.
    Args:
        ticker: Stock ticker symbol (e.g. "AAPL"). Must be a US-listed company available on SEC EDGAR.
        year: Fiscal year as a string (e.g. "2023").
    Returns:
        A list of  year, concept and values from the 10k fillings.
    """
    concepts= []
    # Filter by form type
    j = 2025-int(year)
    tenk_filings = Company(ticker).get_filings(form="10-K")[j]
    # Parse XBRL data
    xbrl = tenk_filings.xbrl()
    if xbrl is None:
        return None
    ist = xbrl.statements.income_statement()
    ist_data = get_from_income_statement(ist, year)  
    concepts.append(ist_data)
    bs = xbrl.statements.balance_sheet()
    bs_data = get_from_balance_sheet(bs, year)
    concepts.append(bs_data)
    return concepts


if __name__ == "__main__":
    set_identity("your.name@example.com")
    database = os.path.join("data", "RL_database.db")

    companies = {
        "AAPL": "Apple",
        "MSFT": "Microsoft",
        "GOOGL": "Google",
        "META": "Meta",
        "AMZN": "Amazon",
        "NFLX": "Netflix",
        "CRM": "Salesforce",
        "ORCL": "Oracle",
        "INTC": "Intel",
        "IBM": "IBM",
        # Semiconductors / hardware
        "NVDA": "NVIDIA", 
        "AMD": "AMD",
        "AVGO": "Broadcom",
        "QCOM": "Qualcomm",
        "TXN": "Texas Instruments",
        # Big tech / platforms
        "ADBE": "Adobe",
        "CSCO": "Cisco",
        "SAP": "SAP",
        "UBER": "Uber",
        "SHOP": "Shopify",
        # Fintech / payments
        "PYPL": "PayPal",
        "V": "Visa",
        "MA": "Mastercard",
        # Cloud / data / enterprise
        "SNOW": "Snowflake",
        "PLTR": "Palantir",
        "NOW": "ServiceNow",
        "WDAY": "Workday",
        # Consumer tech / growth
        "TSLA": "Tesla",
        "DIS": "Disney",
        "SPOT": "Spotify",
        # China tech (optional but useful)
        "BABA": "Alibaba",
        "JD": "JD.com",
        "PDD": "PDD Holdings" }

    years = ['2025', '2024', '2023', '2022', '2021', '2020', '2019', '2018', '2017', '2016', '2015']
    for ticker, company_name in companies.items():
        for j in range(10):
            # Filter by form type
            if record_exists(database, ticker,years[j]) !=True:
                try:
                    tenk_filings = Company(ticker).get_filings(form="10-K")[j]
                except IndexError:
                    continue
                concepts = get_concepts(ticker, years[j])
                if concepts is None:
                    print('No concepts')
                    continue
                concept_values = {item[1]: item[2] for sublist in concepts for item in sublist}
                #print(concept_values)
                add_record(database, ticker, company_name, years[j], concept_values)
                print(concept_values)
            else:
                print('Record in table ', ticker, years[j])

    conn = sqlite3.connect(database)
    df = pd.read_sql("SELECT * FROM tenk_concepts", conn)
    conn.close()
    print(df)
        