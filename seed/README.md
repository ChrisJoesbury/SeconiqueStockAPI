# SeconiqueStockAPI › seed

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange)
![CSV](https://img.shields.io/badge/Data-CSV-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-success)

The `seed` folder contains the scripts and data needed to update the `api_stocklevels` table in the MySQL database used by SeconiqueStockAPI.

These resources support development, testing, data QA, and production reseeding.

**Tested on:** Python 3.11+, pandas, SQLAlchemy, PyMySQL; MySQL 8.x. (Application stack: Python 3.13+, Django 6.0.1 — see root README.)

---

## 📁 Files Included

### **1. dataseed.py**
A Python script designed to run inside the **PythonAnywhere Bash console**. This script:

- Loads the `stocklevels.csv` file using pandas.
- Connects to MySQL using SQLAlchemy + PyMySQL.
- Automatically appends a `lastUpdatedDT` timestamp column using `datetime.utcnow()`.
- Inserts all records into the **`api_stocklevels`** table using `.to_sql()` with `if_exists="append"`.
- Prints the number of imported rows.
- Closes the database connection cleanly.

**Usage:**
```bash
python dataseed.py
```

---

### **2. stocklevels.csv**
A CSV file containing **5,000+ stock level records**. Each row represents a product entry with core fields used by the Stock API.

CSV Columns:
- `company` – Supplier prefix
- `partNum` – Product part number / SKU
- `partDesc` – Product description
- `rangeName` – Product range name
- `groupDesc` – Product group description
- `subGroupDesc` – Sub‑group / category
- `stockLev` – Current stock level (integer)

---

## 🗄️ Database Schema Overview
The MySQL table `api_stocklevels` is populated from the CSV data plus an additional timestamp column added by `dataseed.py`.

### Schema Structure (based on files provided)
| Column Name     | Type        | Source |
|-----------------|-------------|--------|
| company         | VARCHAR     | CSV |
| partNum         | VARCHAR     | CSV |
| partDesc        | VARCHAR     | CSV |
| rangeName       | VARCHAR     | CSV |
| groupDesc       | VARCHAR     | CSV |
| subGroupDesc    | VARCHAR     | CSV |
| stockLev        | INT         | CSV |
| lastUpdatedDT   | DATETIME    | Added by dataseed.py |
