#======================================================
# Import packages and libraries
#======================================================
import numpy as np
import pandas as pd
import pyodbc
from sklearn.preprocessing import StandardScaler
import joblib

#======================================================
#Read data from SQL Server
#======================================================

conn = pyodbc.connect(
    'Driver={SQL Server};'
    'Server=ghosh;'
    'Database=BankChurn;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

query = """
SELECT
    d.Gender, d.Age, l.[Geography], d.Salary,
    a.Tenure, a.Balance, a.NumProducts, a.HasCreditCard, a.IsActive,
    d.Churned
FROM demographic d
JOIN account a ON d.CustomerId = a.CustomerId
JOIN location l ON d.LocationId = l.LocationId
"""

df = pd.read_sql(query, conn)

#======================================================
#Split Train and Test Data
#======================================================

FRAC = 0.8
SEED = 200

df_train = df.sample(frac=FRAC, random_state=SEED)
df_test = df.drop(df_train.index)
print(f"Train Data Shape: {df_train.shape}")
print(f"Test Data Shape: {df_test.shape}")

#======================================================
#Feature Engineering in Train Data
#======================================================

df_train['BalanceSalaryRatio'] = df_train['Balance'] / df_train['Salary']
df_train['TenureByAge'] = df_train['Tenure'] / df_train['Age']

#======================================================
#Encoding Numerical Variables in Train Data
#======================================================

num_cols = df_train.select_dtypes(include=['int64', 'float64']).columns
scaler = StandardScaler()
df_train[num_cols] = scaler.fit_transform(df_train[num_cols])

#======================================================
#Encoding Categorical Variables in Train Data
#======================================================

cat_cols = df_train.select_dtypes(include=['object', 'string', 'bool']).columns.drop('Churned')

for col in cat_cols:
    for val in df_train[col].unique():
        df_train[f"{col}_{val}"] = np.where(df_train[col] == val, 1, 0)

df_train = df_train.drop(columns=cat_cols)

#======================================================
#Preprocessing Pipeline in Testing
#======================================================

def DfTestPipeline(df_test):
    df_test['BalanceSalaryRatio'] = df_test['Balance'] / df_test['Salary']
    df_test['TenureByAge'] = df_test['Tenure'] / df_test['Age']

    df_test[num_cols] = scaler.transform(df_test[num_cols])

    for col in cat_cols:
        for val in df_test[col].unique():
            df_test[f"{col}_{val}"] = np.where(df_test[col] == val, 1, 0)

    df_test = df_test.drop(columns=cat_cols)

    return df_test

df_test = DfTestPipeline(df_test)

#======================================================
# Re-order Columns in Train and Test Data
#======================================================

df_train.columns.equals(df_test.columns)
df_test = df_test[df_train.columns]

#======================================================
# Declare Features and Targets
#======================================================
df_train_x = df_train.drop('Churned', axis=1)
df_train_y = df_train['Churned']

df_test_x = df_test.drop('Churned', axis=1)
df_test_y = df_test['Churned']

#=====================================================
# Save Data
#=====================================================

artifacts = {
    "X_train": df_train_x,
    "y_train": df_train_y,
    "X_test": df_test_x,
    "y_test": df_test_y
}

joblib.dump(artifacts, 'dataset_bundle.pkl')