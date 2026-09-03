#import libraries and modules
from pathlib import Path
import pandas as pd
import pyodbc

#load cleaned demographic data
BASE_DIR = Path(__file__).resolve().parents[2]
FILE_NAME = "cleaned_demographic.csv"
DATA_PATH = BASE_DIR / "data" / "processed" / FILE_NAME
df_demographic = pd.read_csv(DATA_PATH)

#load cleaned account data
FILE_NAME = "cleaned_account.csv"
DATA_PATH = BASE_DIR / "data" / "processed" / FILE_NAME
df_account = pd.read_csv(DATA_PATH)

#load cleaned location data
FILE_NAME = "cleaned_location.csv"
DATA_PATH = BASE_DIR / "data" / "processed" / FILE_NAME
df_location = pd.read_csv(DATA_PATH)

#connect to SQL database
conn = pyodbc.connect(
    'Driver={SQL Server};'
    'Server=ghosh;'
    'Database=BankChurn;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()


#push demographic data to SQL database
cursor.execute("SET IDENTITY_INSERT demographic OFF;")
conn.commit()

for index, row in df_demographic.iterrows():
    cursor.execute("""
        INSERT INTO demographic (
            CustomerId,
            Gender,
            Age,
            Salary,
            LocationId,
            Churned
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    int(row.CustomerId),
    row.Gender,
    int(row.Age),
    float(row.Salary),
    int(row.LocationId),
    int(row.Churned)
    )

    conn.commit()
    print(f"Inserted row {index + 1} into the demographic table.")
                   
#push account data to SQL database

for index, row in df_account.iterrows():
    cursor.execute("""
        INSERT INTO account (
            CustomerId,
            Tenure,
            Balance,
            NumProducts,
            HasCreditCard,
            IsActive
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """,
    int(row.CustomerId),
    int(row.Tenure),
    float(row.Balance),
    int(row.NumProducts),
    int(row.HasCreditCard),
    int(row.IsActive)
    )

    conn.commit()
    print(f"Inserted row {index + 1} into the account table.")


#push location data to SQL database
cursor.execute("SET IDENTITY_INSERT location OFF;")
conn.commit()

for index, row in df_location.iterrows():
    cursor.execute("""
        INSERT INTO location (
            LocationId,
            Geography
        )
        VALUES (?, ?)
    """,
    int(row.LocationId),
    row.Geography
    )

    conn.commit()
    print(f"Inserted row {index + 1} into the location table.")