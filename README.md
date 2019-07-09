# ReyesVerifier - Web

Data verification tool for Reyes Beverage Group

Setup: Install all dependencies with pip install -r requirements.txt

Currently checks files with a Bootstrap/Flask powered web UI for:
- Labels correct and in the right order, based on what file type it is (INVENTORY, SALES, PAYROLL, etc.)
- The rows are all filled out (there isn't a row missing some columns)
- Company IDs consist of letters only (regex) and length > 2
- Dates are all in proper date format
- Costs are all numbers between 1000 and 50000
- All columns that are supposed to be numeric are numeric (almost)
