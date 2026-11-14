# Bank Customer Churn Prediction

End-to-end churn pipeline for retail banking: Excel → cleaning → SQL Server → SQL EDA → statistical tests → four benchmarked classifiers.

| 10,000 customers | 20.4% churn | 19 model features | 4 models benchmarked | Best ROC-AUC |
|:---:|:---:|:---:|:---:|:---:|
| 6 countries | 3.9 : 1 imbalance | 9 inputs + 2 engineered | LogReg · RF · SVM · XGBoost | **0.838 (XGBoost)** |

---

## Key Findings

- **Age is the strongest signal.** Churn is 7.6% under 30, 19.0% at 30–50 and **44.6% over 50** (56.0% for ages 50–59).
- **Product count is U-shaped.** 1 product: 27.7% · **2 products: 7.6%** · 3 products: 82.7% · 4 products: 100% (only 60 customers).
- **Inactive members churn almost twice as often:** 26.9% vs 14.3% (χ² = 243, p < 0.001).
- **Women churn more than men:** 25.1% vs 16.5%.
- **No effect:** geography (19.4%–21.1%), credit card ownership (20.8% vs 20.2%), salary, and balance level.
- **XGBoost ranks best.** Its top-scored 10% of customers contain **40.9% of all churners** (4.1× lift).

---

## Dataset

| Item | Detail |
|---|---|
| Source tables | `Demographic`, `Account`, `Location` (sheets of `data/raw/raw_data.xlsx`) |
| Target | `Churned` (1 = churned, 0 = retained): 2,037 vs 7,963 customers |
| Geographies | Germany, France, Spain, UK, Canada, USA |
| Inputs | `Gender`, `Age` (18–92), `Salary`, `Geography`, `Tenure` (0–10), `Balance`, `NumProducts` (1–4), `HasCreditCard`, `IsActive` |
| Engineered | `BalanceSalaryRatio = Balance / Salary`, `TenureByAge = Tenure / Age` |
| Missing data | `Balance` null in **3,617 rows (36.2%)**, filled with the mean (119,827.49) |
| Dropped | `Name`, `AccountId` |

---

## Pipeline

```
raw_data.xlsx ─► cleaning scripts ─► 3 cleaned CSVs ─► SQL Server (BankChurn)
                                                          │
                       ┌──────────────────────────────────┼───────────────────────┐
                       ▼                                  ▼                       ▼
                 EDA SQL queries                 statistical tests         preprocessing.py
                                                                                  │
                                                                                  ▼
                                                                      dataset_bundle.pkl
                                                                                  │
                                                                                  ▼
                                                              5 model notebooks (+ evaluation script)
```

1. **Clean:** validate types and categories, impute `Balance`, drop identifiers.
2. **Ingest:** load into three SQL Server tables (`demographic`, `account`, `location`).
3. **Explore:** T-SQL with CTEs, a window function and a parameterised filter.
4. **Preprocess:** join in SQL, 80/20 split (`random_state=200`: 8,000 train / 2,000 test), engineer ratios, `StandardScaler` (fit on train only), one-hot encode.
5. **Model:** `GridSearchCV` optimising F1 with class weighting for imbalance.

---

## Model Performance

Test set: 2,000 customers, 374 churners (18.7%). Default 0.5 cutoff.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 68.6% | 32.8% | 65.2% | 43.7% | 0.743 | 0.396 |
| Random Forest | **81.5%** | **50.4%** | 63.6% | **56.3%** | 0.828 | 0.614 |
| SVM (RBF) | 79.0% | 46.0% | **71.9%** | 56.1% | 0.829 | 0.631 |
| **XGBoost** | 79.4% | 46.4% | 67.9% | 55.2% | **0.838** | **0.649** |
| SVM (Poly) | not completed | | | | | |

**Confusion matrices** (churn = positive):

| Model | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| Logistic Regression | 1,127 | 499 | 130 | 244 |
| Random Forest | 1,392 | 234 | 136 | 238 |
| SVM (RBF) | 1,310 | 316 | 105 | 269 |
| XGBoost | 1,333 | 293 | 120 | 254 |

**Best hyperparameters**

| Model | Settings |
|---|---|
| Logistic Regression | `C=0.1`, `penalty='l2'`, `class_weight='balanced'` |
| Random Forest | 300 trees, `max_depth=15`, `min_samples_leaf=4`, `min_samples_split=10`, `class_weight='balanced'` |
| SVM (RBF) | `C=1`, `gamma='auto'`, `class_weight='balanced'` |
| XGBoost | `n_estimators=20`, `max_depth=5`, `learning_rate=0.3`, `min_child_weight=10`, `gamma=0.1`, `subsample=1`, `colsample_bytree=1`, `scale_pos_weight=3.81` |

**Takeaways**

- XGBoost has the best ranking quality (ROC-AUC 0.838, PR-AUC 0.649). The gap to Random Forest and SVM-RBF is about 0.01 AUC on only 374 churners, so treat it as a lead, not a landslide.
- Accuracy is misleading here: predicting "nobody churns" scores 81.3%. Class weighting lowers accuracy but lifts recall from roughly 16–43% (unweighted runs) to **64–72%**.
- Moving XGBoost's cutoff trades precision for recall:

| Cutoff | Recall | Precision | Customers flagged |
|---:|---:|---:|---:|
| 0.3 | 86.9% | 31.6% | 1,030 |
| 0.5 | 67.9% | 46.4% | 547 |
| 0.7 | 53.2% | 62.6% | 318 |

**Top features** (importance): Random Forest: `Age` 0.299, `NumProducts` 0.178, `TenureByAge` 0.095. XGBoost: `NumProducts` 0.206, `Age` 0.195, `IsActive_True` 0.171.

---

## Statistical Testing

| Test | Question | Result | Effect size | Verdict |
|---|---|---|---|---|
| Welch's t-test | Balance: churned vs retained | 120,521 vs 119,650; t = 1.35, p = 0.176 | Cohen's d = 0.036 | Not significant |
| Chi-square | `IsActive` vs churn | χ² = 242.99, df = 1, p ≈ 9e-55 | Cramér's V = 0.156 | **Significant**, modest effect |
| One-way ANOVA | Tenure across countries | F = 0.915, p = 0.470 | η² = 0.0005 | Not significant |

Levene's test showed unequal balance variances (p ≈ 1e-9), which is why Welch's t-test was used.

---

## SQL Analysis

| Query | Purpose | Result |
|---|---|---|
| `EDA.sql` | Churn by gender | Female 25.1%, Male 16.5% |
| `EDA2.sql` | Churn by country × age group | Over-50s churn 40.7%–49.3% in every country; under-30s 5.7%–9.8% |
| `EDA3.sql` | Parameterised filter (`@MinTenure`, `@MaxBalance`, `@MaxProducts`) | 219 customers with tenure > 2, balance < 70,000, products < 3 (25.1% churn) |

---

## Repository Structure

```
Bank-Customer-Churn-Prediction/
├── data/
│   ├── raw/raw_data.xlsx                  # 3 sheets: Demographic, Location, Account
│   └── processed/                         # cleaned_demographic / account / location CSVs
├── scripts/
│   ├── data_cleaning/                     # functions.py, demographic.py, Account.py, location.py
│   └── data_ingestion/sql_connection.py   # CSV → SQL Server
├── eda_queries/                           # EDA.sql, EDA2.sql, EDA3.sql
├── statistical_testing/
│   └── statistical_testing.ipynb          # t-test, chi-square, ANOVA + effect sizes
├── predictive_modelling/
│   ├── processed_data/
│   │   ├── preprocessing.py               # features, scaling, encoding, split
│   │   └── dataset_bundle.pkl             # X_train / y_train / X_test / y_test
│   └── experiments/
│       ├── exp_LogisticReg.ipynb
│       ├── exp_RandomForest.ipynb
│       ├── exp_SVM_RBF.ipynb
│       ├── exp_SVM_Poly.ipynb             # grid search interrupted
│       ├── exp_XGBoost.ipynb
│       └── evaluation_script.py           # evaluate_model()
└── README.md
```

---

## Tech Stack

Python · pandas · NumPy · scikit-learn · XGBoost · SciPy · seaborn / matplotlib · SQL Server + pyodbc · joblib

---

## Getting Started

```bash
git clone https://github.com/ghosh2608/Bank-Customer-Churn-Prediction.git
cd Bank-Customer-Churn-Prediction
python -m venv myenv && source myenv/bin/activate      # Windows: myenv\Scripts\activate
pip install pandas numpy scikit-learn xgboost scipy seaborn matplotlib pyodbc joblib openpyxl
```

| Step | Command | Needs SQL Server |
|---|---|:---:|
| Clean data | `cd scripts/data_cleaning && python demographic.py && python Account.py && python location.py` | No |
| Load database | `cd scripts/data_ingestion && python sql_connection.py` | Yes |
| Preprocess | `cd predictive_modelling/processed_data && python preprocessing.py` | Yes |
| Train models | Run the notebooks in `predictive_modelling/experiments/` | No |
| Statistical tests | Run `statistical_testing/statistical_testing.ipynb` | Yes |

The pre-built `dataset_bundle.pkl` is included, so the model notebooks run without SQL Server.

---

## Notes and Roadmap

**How to read the metrics.** The notebooks print recall, precision and F1. Accuracy, ROC-AUC, PR-AUC and confusion matrices above were recomputed from the best hyperparameters on `dataset_bundle.pkl`; the recall, precision and F1 match the notebook outputs. `evaluate_model` currently computes ROC-AUC from hard predictions (it should use `predict_proba`), so its printed "ROC_AUC" is a balanced accuracy, not the AUC shown here.

**Known limitations**

- `Balance` imputation: 36.2% of values share one number, and the missingness itself is informative (13.8% churn when null vs 24.1% otherwise).
- Single, unstratified 80/20 split with no confidence intervals; the cutoff is the default 0.5.
- Static snapshot with no dates, so `IsActive` and `NumProducts` may partly reflect customers already leaving.
- The fitted scaler and models are not saved, and `evalutaion_script.py` is a duplicate of `evaluation_script.py`.

**Next steps:** `Balance_missing` flag, stratified split with repeated CV, cost-based cutoff selection, probability calibration, SHAP explanations, a scikit-learn `Pipeline`, and a FastAPI/Streamlit scoring app.
