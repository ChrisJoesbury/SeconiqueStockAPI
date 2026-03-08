# api/migrations/

This directory contains Django's automatically generated database migration files. Each file represents a versioned change to the database schema.

Migrations are applied in order and should **always be committed to the repository** so the schema stays in sync across all environments. **Tested on:** Django 6.0.1; SQLite (development/tests) and MySQL 8.x (production).

---

## 📋 Migration History

| Migration | Description |
|---|---|
| `0001_initial` | Initial schema — creates the `stocklevels` table |
| `0002_stocklevels_stocklev` | Adds the `stockLev` (stock level) field |
| `0003_...` | Adds `company` field and `excludefsf` flag to `stocklevels` |
| `0004_groupdescview_subgroupdescview` | Adds unmanaged models for `groupDescView` and `subGroupDescView` DB views |
| `0005_rangenameview` | Adds unmanaged model for `rangeNameView` DB view |
| `0006_userprofile` | Creates the `UserProfile` model linked to Django's `User` |
| `0007_userprofile_custid` | Adds `custid` field to `UserProfile` |
| `0008_rename_custid_...` | Renames `custid` to `cust_ID` |
| `0009_userprofile_website_address` | Adds `website_address` field to `UserProfile` |
| `0010_rename_website_address_...` | Renames `website_address` to `website` |
| `0011_userprofile_company_id` | Adds `company_ID` field to `UserProfile` |
| `0012_remove_stocklevels_excludefsf` | Removes the `excludefsf` field from `stocklevels` |
| `0013_remove_stocklevels_inactive` | Removes the `inactive` field from `stocklevels` |
| `0014_sitesettings` | Creates the `SiteSettings` singleton model |
| `0015_userprofile_company_name` | Adds `company_Name` field to `UserProfile` |
| `0016_rename_stocklevels_to_StockLevels` | Renames `stocklevels` table/model to `StockLevels` |

---

## 🛠️ Common Commands

```bash
# Apply all pending migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations

# Create a new migration after editing models.py
python manage.py makemigrations
```
