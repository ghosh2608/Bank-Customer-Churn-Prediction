# Bank Customer Churn Prediction

An end-to-end machine learning pipeline for predicting customer churn in the banking sector. The project covers data cleaning, SQL-based exploratory analysis, feature engineering, statistical hypothesis testing, and benchmarking of five classification models.

---

## Table of Contents

- [Overview](#overview)
- [Dataset](#dataset)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Methodology](#methodology)
- [Model Performance](#model-performance)
- [Statistical Testing](#statistical-testing)
- [Getting Started](#getting-started)

---

## Overview

Customer churn is a critical metric for banks — acquiring new customers costs significantly more than retaining existing ones. This project builds a predictive model to identify customers likely to leave, enabling proactive retention strategies.

**Key highlights:**
- 10,000 customer records across 6 geographies
- 12 raw features engineered into 19 model-ready features
- 5 classification models trained and benchmarked
- 3 statistical hypothesis tests conducted with effect size analysis

---

## Dataset

| Attribute | Detail |
|---|---|
| Records | 10,000 customers |
| Source Tables | Demographic, Account, Location |
| Geographies | Germany, France, Spain, UK, Canada, USA |
| Target Variable | `Churned` (binary: 0 = Retained, 1 = Churned) |
| Churn Rate | ~20.4% (imbalanced — 3.8:1 ratio) |

### Features

| Feature | Type | Description |
|---|---|---|
| Gender | Categorical | Male / Female |
| Age | Numerical | Customer age (18–92) |
| Salary | Numerical | Estimated salary |
| Geography | Categorical | Country of residence |
| Tenure | Numerical | Years with the bank (0–10) |
| Balance | Numerical | Account balance |
| NumProducts | Numerical | Number of bank products held (1–4) |
| HasCreditCard | Binary | Whether the customer has a credit card |
| IsActive | Binary | Whether the customer is an active member |

### Engineered Features

| Feature | Formula |
|---|---|
| BalanceSalaryRatio | Balance / Salary |
| TenureByAge | Tenure / Age |

---

## Project Structure

```
Bank Churn Project/
│
├── data/
│   ├── raw/                        # Original dataset (Excel)
│   │   └── raw_data.xlsx
│   └── processed/                  # Cleaned CSVs
│       ├── cleaned_demographic.csv
│       ├── cleaned_account.csv
│       └── cleaned_location.csv
│
├── scripts/
│   ├── data_cleaning/              # Data validation & cleaning
│   │   ├── functions.py            # Reusable utility functions
│   │   ├── demographic.py
│   │   ├── Account.py
│   │   └── location.py
│   └── data_ingestion/             # SQL Server data loading
│       └── sql_connection.py
│
├── eda_queries/                    # SQL-based exploratory analysis
│   ├── EDA.sql                     # Churn rate by gender
│   ├── EDA2.sql                    # Churn by geography × age segment
│   └── EDA3.sql                    # Parameterized customer filtering
│
├── predictive_modelling/
│   ├── processed_data/
│   │   ├── preprocessing.py        # Feature engineering & scaling
│   │   └── dataset_bundle.pkl      # Serialized train/test splits
│   └── experiments/
│       ├── exp_LogisticReg.ipynb
│       ├── exp_RandomForest.ipynb
│       ├── exp_SVM_RBF.ipynb
│       ├── exp_SVM_Poly.ipynb
│       ├── exp_XGBoost.ipynb
│       └── evaluation_script.py    # Standardized evaluation metrics
│
├── statistical_testing/
│   └── statistical_testing.ipynb   # t-test, Chi-Square, ANOVA
│
└── .gitignore
```

---

## Tech Stack

| Layer | Tools |
|---|---|
| Language | Python 3.14 |
| Data Processing | Pandas, NumPy |
| Database | Microsoft SQL Server, pyodbc |
| Machine Learning | scikit-learn, XGBoost |
| Statistical Analysis | SciPy |
| Visualization | Seaborn, Matplotlib |
| Serialization | Joblib |

---

## Methodology

### 1. Data Cleaning
- Validated data types and categorical values using reusable utility functions
- Imputed missing `Balance` values with column mean
- Removed non-predictive columns (`Name`, `AccountId`)
- Exported cleaned data to CSV for downstream use

### 2. Data Ingestion
- Loaded cleaned data into a normalized SQL Server database (3 tables: `demographic`, `account`, `location`)
- Enabled SQL-based exploratory analysis with JOINs across tables

### 3. Exploratory Data Analysis (SQL)
- Analyzed churn rate segmented by gender, geography, and age groups
- Used CTEs, window functions, and parameterized queries

### 4. Preprocessing & Feature Engineering
- Created `BalanceSalaryRatio` and `TenureByAge` as interaction features
- Applied `StandardScaler` normalization on numerical features
- One-hot encoded categorical variables (`Gender`, `Geography`, `HasCreditCard`, `IsActive`)
- 80/20 train-test split (random state = 200)

### 5. Model Training & Evaluation
- Trained 5 classification models with standardized evaluation
- Metrics: Accuracy, Precision, Recall, F1-Score, ROC-AUC

---

## Model Performance

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 82.25% | 59.60% | 15.78% | 24.95% | 0.7414 |
| Random Forest | 85.65% | 71.43% | 38.77% | 50.26% | 0.8097 |
| SVM (RBF Kernel) | 86.35% | **81.76%** | 34.76% | 48.78% | 0.8032 |
| SVM (Poly Kernel) | 86.30% | 82.47% | 33.96% | 48.11% | — |
| **XGBoost** | 85.05% | 64.94% | **43.58%** | **52.16%** | **0.8098** |

**Best overall model:** XGBoost — highest ROC-AUC (0.81), best F1-Score (0.52), and strongest recall for identifying churners.

### Top Predictive Features

| Rank | Random Forest | XGBoost |
|---|---|---|
| 1 | Age (0.222) | NumProducts (0.269) |
| 2 | NumProducts (0.120) | IsActive (0.183) |
| 3 | Salary (0.117) | Age (0.115) |

---

## Statistical Testing

Three hypothesis tests were conducted to validate feature–churn relationships:

### Welch's t-test — Balance vs. Churn
| Metric | Value |
|---|---|
| Churned Mean Balance | $120,521 |
| Retained Mean Balance | $119,650 |
| t-statistic | 1.353 |
| p-value | 0.176 |
| Cohen's d | 0.036 |
| **Conclusion** | **No significant difference** — balance alone does not predict churn |

### Chi-Square Test — IsActive vs. Churn
| Metric | Value |
|---|---|
| χ² Statistic | 242.99 |
| p-value | < 0.001 |
| Degrees of Freedom | 1 |
| Cramér's V | 0.156 |
| **Conclusion** | **Statistically significant** — inactive customers churn at a substantially higher rate |

### One-Way ANOVA — Tenure across Geographies
| Metric | Value |
|---|---|
| F-statistic | 0.915 |
| p-value | 0.470 |
| η² (Eta Squared) | 0.0005 |
| **Conclusion** | **No significant difference** — tenure does not vary meaningfully across countries |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Microsoft SQL Server (for data ingestion and EDA queries)

### Installation

```bash
git clone https://github.com/ghosh2608/Bank-Customer-Churn-Prediction.git
cd Bank-Customer-Churn-Prediction

python -m venv myenv
myenv\Scripts\activate        # Windows
source myenv/bin/activate     # macOS/Linux

pip install pandas numpy scikit-learn xgboost scipy seaborn matplotlib pyodbc joblib openpyxl
```

### Running the Pipeline

1. **Data Cleaning** — Run the cleaning scripts to regenerate processed CSVs:
   ```bash
   cd scripts/data_cleaning
   python demographic.py
   python Account.py
   python location.py
   ```

2. **Data Ingestion** *(requires SQL Server)* — Load cleaned data into the database:
   ```bash
   cd scripts/data_ingestion
   python sql_connection.py
   ```

3. **Preprocessing** *(requires SQL Server)* — Generate the train/test dataset bundle:
   ```bash
   cd predictive_modelling/processed_data
   python preprocessing.py
   ```

4. **Model Experiments** — Open and run the Jupyter notebooks in `predictive_modelling/experiments/`

5. **Statistical Testing** — Open and run `statistical_testing/statistical_testing.ipynb`

> **Note:** The pre-built `dataset_bundle.pkl` is included in the repository, so you can run the experiment notebooks directly without needing SQL Server.

---
