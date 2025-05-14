from flask import Flask, render_template
from data_processor import process_multiple_mps
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

app = Flask(__name__)

@app.route('/')
def dashboard():
    files = {
        'MP3': r"o:\Fabricacao\1 - MP03\1 - CEP\01 - CEP\CEP MP#03-Checklist.xlsm",
        'MP4': r"O:\Fabricacao\2 - MP04\1-CEP\CEP MP#04 v2.xlsm",
        'MP8': r"O:\Fabricacao\3 - MP08\1 - CEP\01 - CEP\CEP MP#08-Checklist.xlsm",
        'MP12': r"O:\Fabricacao\4 - MP12\1 - CEP\CEP MP#12-Checklist.xlsm"
    }
    for name, path in files.items():
        if not os.path.exists(path):
            return render_template('dashboard.html', data=None, error=f"Arquivo '{path}' não encontrado.")
    data = process_multiple_mps(files)
    return render_template('dashboard.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)