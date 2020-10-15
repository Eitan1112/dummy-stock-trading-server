import yfinance as yf
from flask import Flask, request
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

@app.route('/invest', methods=['POST'])
def invest():
    # Parse json
    with open(DATABASE_FILENAME, 'r') as f:
        data = f.read()

    balance = json.loads(data)['balance']
    investments = json.loads(data)['investments']

    # Parse request variables
    company = request.form.get('company')
    sum = request.form.get('sum')
    if(sum is None):
        sum = balance
    else:
        sum = int(sum)

    # Reduce Balance
    balance -= sum
    
    # Verify balance
    if(balance < 0):
        return f"Cannot get to negative balance {balance}"

    # Add Investment
    stock_price = get_current_stock_price(company)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    investments.append({
        "company": company,
        "stock_price": stock_price,
        "sum": sum,
        "investment_timestamp": timestamp,
        "withdrawl_cash": None,
        "active": True
    })

    # Save to file
    with open(DATABASE_FILENAME, 'w') as f:
        f.write(json.dumps({
            "balance": balance,
            "investments": investments
        }))
    
    return 'OK'

@app.route('/cash_out', methods=['POST'])
def cash_out_last_investment():
    # Parse json
    with open(DATABASE_FILENAME, 'r') as f:
        data = f.read()

    balance = json.loads(data)['balance']
    investments = json.loads(data)['investments']

    # Verify there are investments
    if(len(investments) == 0):
        return "No investments"

    # Get last investment
    investment = investments[-1]

    # Verify last investment
    if(investment['active'] == False):
        return "No active stock investment"

    # Check current stock price
    current_stock_price = get_current_stock_price(investment['company'])

    # Calculate profit
    prev_stock_price = investment['stock_price']
    withdrawl_cash = (current_stock_price / prev_stock_price) * investment['sum']

    # Add to balance
    balance += withdrawl_cash

    # Disable last investment
    investments[-1]['active'] = False

    # Add cashout sum
    investments[-1]['withdrawl_cash'] = withdrawl_cash

    # Save data to file
    with open(DATABASE_FILENAME, 'w') as f:
        f.write(json.dumps({
            "balance": balance,
            "investments": investments
        }))
    
    return 'OK'


if(__name__ == '__main__'):
    app.run('0.0.0.0', debug=True)
    