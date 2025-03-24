import pandas as pd

FILE_PATH = "data.xlsx"
xls = pd.ExcelFile(FILE_PATH)

DF_PV = pd.read_excel(xls, sheet_name="PV")
DF_EV = pd.read_excel(xls, sheet_name="EV")
DF_AC = pd.read_excel(xls, sheet_name="AC")
BARRAS = pd.read_excel(xls, sheet_name="BARRAS")
MESES = pd.read_excel(xls, sheet_name="MESES")

