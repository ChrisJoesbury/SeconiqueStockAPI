# SeconiqueStockAPI › docs

![Database](https://img.shields.io/badge/Database-MySQL-blue)
![DDL](https://img.shields.io/badge/Type-Sanitised%20DDL%20Schema-purple)
![Status](https://img.shields.io/badge/Docs-Updated-success)

This folder contains the **sanitised database schema documentation** for SeconiqueStockAPI. This version excludes all Django framework tables, internal metadata, definers, and environment‑specific details. It includes **only the API‑related tables and views**, making it safe for public repositories.

---

## 📁 Files Included

### **1. [SeconiqueStockAPI User Manual v1-001.pdf](SeconiqueStockAPI%20User%20Manual%20v1-001.pdf)**
End-user manual for the SeconiqueStockAPI application.

### **2. [SeconiqueStockAPI Admin User Manual v1-001.pdf](SeconiqueStockAPI%20Admin%20User%20Manual%20v1-001.pdf)**
Administrator manual for managing and configuring the SeconiqueStockAPI application.

### **3. DatabaseSchema_sanitised.sql**
This SQL file contains a **clean, public‑safe MySQL schema**, defining only the tables and views required for SeconiqueStockAPI operation.

Included:
- `api_stocklevels`
- `api_userprofile`
- `api_sitesettings`
- Views: `groupDescView`, `rangeNameView`, `subGroupDescView`

Removed:
- Django auth tables
- Django admin/session/log tables
- Foreign key references to Django tables
- MySQL dump metadata
- DEFINER clauses

---

## 🗄️ Key Tables

### **api_stocklevels**
Stores the stock level information consumed by the API.

| Column         | Type          | Description |
|----------------|---------------|-------------|
| id             | bigint, PK    | Auto‑incrementing ID |
| partNum        | varchar(11)   | Product SKU |
| partDesc       | varchar(150)  | Product description |
| lastUpdatedDT  | datetime(6)   | Import timestamp |
| stockLev       | int           | Current stock level |
| company        | varchar(10)   | Supplier/company code |
| groupDesc      | varchar(100)  | Product group |
| rangeName      | varchar(100)  | Product range |
| subGroupDesc   | varchar(100)  | Product subgroup |

---

### **api_userprofile**
Maps users to customer metadata used by the API.

| Column         | Type          | Description |
|----------------|---------------|-------------|
| id             | bigint, PK    | Auto‑incrementing ID |
| api_key        | varchar(255)  | Assigned API key (hashed) |
| user_id        | int           | User reference (external system) |
| cust_ID        | varchar(6)    | Customer identifier |
| website        | varchar(255)  | Customer website |
| company_ID     | varchar(10)   | Customer company code |
| company_Name   | varchar(100)  | Customer company name |

---

### **api_sitesettings**
Simple key/value configuration table.

| Column               | Type         |
|----------------------|--------------|
| id                   | bigint, PK   |
| registration_enabled | tinyint(1)   |

---

## 👁️ Views Included
All views derive from `api_stocklevels`.

### **groupDescView**
Distinct, ordered product groups.

### **rangeNameView**
Distinct, ordered product ranges.

### **subGroupDescView**
Distinct, ordered product subgroups.

These views improve:
- Filtering performance
- Autocomplete lookups
- Data integrity for UI/API consumers

---

## 📌 Usage
You can deploy this schema into any MySQL 8.x database:
```sql
mysql -u <user> -p <database> <DatabaseSchema_sanitised.sql>
```

This schema is suitable for:
- Public repos
- Documentation sites
- Third‑party integrators
- Testing environments

---

## 📄 Notes
- This is the **sanitised** database schema derived from the production DDL.
- All sensitive or framework‑related components have been removed.
- Designed to reflect only API‑critical tables and views.
