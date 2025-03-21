import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
# from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
import pandas as pd
from backend.helpers.query_system import EthicalInvestmentQuerySystem, load_stock_data

# ROOT_PATH for linking with all your files. 
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..",os.curdir))

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

# Specify the path to the JSON file relative to the current script
json_file_path = os.path.join(current_directory, 'sp500.json')

# Load json data
with open(json_file_path, 'r') as file:
    json_text = file.read()
    stocks_data = load_stock_data(json_text)

query_system = EthicalInvestmentQuerySystem(stocks_data)

app = Flask(__name__)
CORS(app)

@app.route('/query', methods=['GET'])
def query_endpoint():
    user_query = request.args.get('query', default='', type=str)
    results = query_system.rank_stocks(stocks_data, user_query)
    return Flask.jsonify(results)

@app.route("/")
def home():
    return render_template('base.html',title="sample html")

if 'DB_NAME' not in os.environ:
    app.run(debug=True,host="0.0.0.0",port=5000)