# Dashboard Web Application

This project is a web-based dashboard application that monitors an Excel file for specific data conditions. It checks the entries in the "BD" sheet of the specified Excel file and provides visual feedback based on the data.

## Project Structure

```
dashboard-app
├── src
│   ├── app.py               # Main entry point of the application
│   ├── data_processor.py     # Contains data processing functions
│   └── templates
│       └── dashboard.html    # HTML template for the dashboard
├── requirements.txt          # Lists project dependencies
└── README.md                 # Documentation for the project
```

## Requirements

To run this application, you need to install the following dependencies:

- Flask
- openpyxl

You can install the required packages using pip:

```
pip install -r requirements.txt
```

## Usage

1. Ensure that the Excel file `CEP MP#04 v2.xlsm` is located at `O:\Fabricacao\2 - MP04\1-CEP\`.
2. Run the application:

```
python src/app.py
```

3. Open your web browser and navigate to `http://127.0.0.1:5000` to view the dashboard.

## Functionality

- The application reads the specified Excel file and processes the data from the "BD" sheet.
- It checks if columns C, D, and E are filled for each entry.
- Displays a green face if all conditions are met, otherwise shows a red face.
- Validates that there are at least 3 entries per day.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.