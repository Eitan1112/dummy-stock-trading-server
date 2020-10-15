import yfinance as yf
from flask import Flask
from datetime import datetime
import json
import os

app = Flask(__name__)
DATABASE_FILENAME = 'data.json'

def get_current_stock_price(company):
    return list(yf.Ticker(company).history(period="max").iterrows())[-1][1].Close

@app.route('/get_balance')
def get_balance():
    with open(DATABASE_FILENAME, 'r') as f:
        data = f.read()
    
    balance = json.loads(data)['balance']
    return balance

@app.route('/invest')
def invest(company, sum):
    
    # Parse json
    with open(DATABASE_FILENAME, 'r') as f:
        data = f.read()

    balance = json.loads(data)['balance']
    investments = json.loads(data)['investments']

    # Reduce Balance
    balance -= sum

    # Add Investment
    stock_price = get_current_stock_price(company)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    investments.append({
        "company": company,
        "stock_price": stock_price,
        "sum": sum,
        "investment_timestamp": timestamp,
        "active": True
    })

    # Save to file
    with open(DATABASE_FILENAME, 'w') as f:
        f.write(json.dumps({
            "balance": balance,
            "investments": investments
        }))
    
    return 'OK'

@app.route('/cash_out')
def cash_out_last_investment():
    # Parse json
    with open(DATABASE_FILENAME, 'r') as f:
        data = f.read()

    balance = json.loads(data)['balance']
    investments = json.loads(data)['investments']

    # Check current stock price
    investment = investments[-1]
    current_stock_price = get_current_stock_price(investment['company'])

    # Calculate profit
    prev_stock_price = investment['stock_price']
    withdrawl_cash = (current_stock_price / prev_stock_price) * investment['sum']

    # Add to balance
    balance += withdrawl_cash

    # Disable last investment
    investments[-1]['active'] = False

    # Save data to file
    with open(DATABASE_FILENAME, 'w') as f:
        f.write(json.dumps({
            "balance": balance,
            "investments": investments
        }))
    
    return 'OK'


if(__name__ == '__main__'):
    app.run('0.0.0.0', debug=True)
    