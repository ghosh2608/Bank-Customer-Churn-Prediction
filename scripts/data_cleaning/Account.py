#Import Modules and Libraries
from pathlib import Path
import pandas as pd
from functions import categorical_sanity_check
from functions import validate_dtypes 
from functions import missing_value_report
from functions import plot_distribution
from functions import plot_boxplot

#File Paths
BASE_DIR = Path(__file__).resolve().parents[2]
FILE_NAME = "raw_data.xlsx"
DATA_PATH = BASE_DIR / "data" / "raw" / FILE_NAME

SHEET_NAME = "Account"
df = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME)

#Categorical Sanity Check
categorical_sanity_check(df,
                          "IsActive", 
                          [0,1])

# Data Type Checking
expected_dtypes = {
    'Tenure': 'int64',
    'Balance': 'float64',
    'NumOfProducts': 'int64',
    'HasCreditCard': 'int64',
    'IsActive': 'int64',
}

validate_dtypes(df, expected_dtypes)

#Null Values Checker
missing_value_report(df)

#Outlier Detection and Distribution
plot_distribution(df, "Balance")
plot_boxplot(df, "Balance")

#Missing Value Imputation
df['Balance'] = df['Balance'].fillna(df['Balance'].mean())

#Remove Columns
df = df.drop(columns=['AccountId'])

#Export File
OUTPUT_DIR = BASE_DIR / "data" / "processed"
file_name = "cleaned_account.csv"
file_path = OUTPUT_DIR / file_name
df.to_csv(file_path, index=False)