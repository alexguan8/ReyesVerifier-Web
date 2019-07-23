# ReyesVerifier - Web

Data verification tool for Reyes Beverage Group

Setup: Install all dependencies with pip install -r requirements.txt

Currently checks files with a Bootstrap/Flask powered web UI for:
- Labels correct and in the right order, based on what file type it is (INVENTORY, SALES, PAYROLL, etc.)
- File name should be formatted properly with correct file type
- The rows are all filled out (there isn't a row missing some columns)
- Every row should be unique (No duplicate rows)
- Company IDs consist of letters only (regex), length > 2, and supposed to be in the CoID table pulled from RBG_DM database
- Dates are all in proper date format
- CostCtrs are all numbers between 1000 and 9999
- All columns that are supposed to be numeric are numeric (almost)
