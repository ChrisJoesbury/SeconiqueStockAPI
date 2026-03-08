# SeconiqueStockAPI › postman

![Postman](https://img.shields.io/badge/Postman-Collection-orange)
![API](https://img.shields.io/badge/API-REST-blue)
![Auth](https://img.shields.io/badge/Auth-API--Key-yellow)
![Status](https://img.shields.io/badge/Status-Active-success)

This folder contains the **Postman collection** for SeconiqueStockAPI. It provides ready-to-use requests for all API endpoints, with pre-configured filter parameters included as disabled examples that can be enabled as needed.

**Tested on:** API running with Django 6.0.1 and Django REST Framework 3.15+; Postman v10+.

---

## 📁 Files Included

### **1. SeconiqueStockAPI.postman_collection.json**
A Postman collection (v2.1) containing all five API endpoints. All requests use collection variables for the base URL and API key — no credentials are hardcoded.

---

## 🚀 Setup

### 1. Import the collection
In Postman, click **Import** and select `SeconiqueStockAPI.postman_collection.json`.

### 2. Set the collection variables
After importing, open the collection and navigate to the **Variables** tab. Set the following:

| Variable | Description | Example |
|---|---|---|
| `url` | Base URL of the API (no trailing slash) | `http://127.0.0.1:8000` |
| `APIKEY` | Your full API key including the `Api-Key ` prefix | `Api-Key abc123.xyz...` |

> **Note:** Your API key can be generated on your profile page at `/profile/` once your account has been verified by an administrator.

---

## 📚 Requests Included

### **GET /prodgroups**
Returns a sorted list of all distinct product group descriptions.

| Parameter | Default | Description |
|---|---|---|
| `limit` | *(disabled)* | Maximum number of records to return |
| `offset` | *(disabled)* | Number of records to skip |

---

### **GET /prodsubgroups**
Returns a sorted list of all distinct product sub-group descriptions.

| Parameter | Default | Description |
|---|---|---|
| `limit` | *(disabled)* | Maximum number of records to return |
| `offset` | *(disabled)* | Number of records to skip |

---

### **GET /ranges**
Returns a sorted list of all distinct product range names.

| Parameter | Default | Description |
|---|---|---|
| `limit` | *(disabled)* | Maximum number of records to return |
| `offset` | *(disabled)* | Number of records to skip |

---

### **GET /stocklevels**
Returns a paginated, filterable list of stock levels in JSON format.

All filter parameters are pre-configured with example values and can be enabled individually in Postman.

| Parameter | Example Value | Description |
|---|---|---|
| `partNum` | `100-101-008` | Filter by exact part number |
| `rangeName` | `CAMBOURNE RANGE` | Filter by range name |
| `groupDesc` | `BEDROOM FURNITURE` | Filter by product group |
| `subGroupDesc` | `WARDROBES` | Filter by sub-group |
| `sl_greaterThan` | `0` | Stock level greater than value |
| `sl_lessThan` | `20` | Stock level less than value |
| `sl_equalTo` | `4` | Stock level equal to value |
| `limit` | `100` | Maximum number of records to return |
| `offset` | `10` | Number of records to skip |

---

### **GET /stocklevels/csv**
Downloads all stock levels for the authenticated customer as a CSV file. No pagination — always returns the full dataset.

---

## 🔑 Authentication

All requests pass the API key via the `Authorization` header using the collection variable `{{APIKEY}}`:

```http
Authorization: Api-Key <your_api_key>
```

This is pre-configured on every request in the collection — you only need to set the `APIKEY` variable once at the collection level.

---

## 📌 Notes

- All filter query parameters in the collection are **disabled by default**. Enable only the filters you need for each request.
- The `url` variable should point to whichever environment you are testing against (local dev, staging, or production) — no changes to individual requests are needed when switching environments.
- Responses are not saved in the collection — run requests live to see current data.
