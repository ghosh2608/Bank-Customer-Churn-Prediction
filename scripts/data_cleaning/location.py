#Import Modules and Libraries
import pandas as pd
from pathlib import Path

## File Paths
BASE_DIR = Path(__file__).resolve().parents[2]
FILE_NAME = "raw_data.xlsx"
DATA_PATH = BASE_DIR / "data" / "raw" / FILE_NAME

SHEET_NAME = "Location"
df = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME)

#Export File
OUTPUT_DIR = BASE_DIR / "data" / "processed"
file_name = "cleaned_location.csv"
file_path = OUTPUT_DIR / file_name
df.to_csv(file_path, index=False)