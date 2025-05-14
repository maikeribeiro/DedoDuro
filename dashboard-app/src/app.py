from flask import Flask, render_template
from data_processor import process_data
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def dashboard():
    excel_path = r"O:\Fabricacao\2 - MP04\1-CEP\CEP MP#04 v2.xlsm"
    if not os.path.exists(excel_path):
        return render_template('dashboard.html', data=None, error=f"Arquivo '{excel_path}' não encontrado.")
    df = pd.read_excel(excel_path, sheet_name='BD Checklist', header=2)
    print("Colunas disponíveis na guia 'BD Checklist':", df.columns.tolist())
    data = process_data(df)
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)