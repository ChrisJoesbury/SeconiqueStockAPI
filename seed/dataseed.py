# =============================================================================
# SeconiqueStockAPI | dataseed.py
# =============================================================================
# Seed script to populate the api_stocklevels MySQL table from stocklevels.csv.
# Truncates existing records before each import to prevent duplicates. Intended
# to be run in a Bash console with credentials set below.
# =============================================================================

#Get pandas to read the CSV file and manipulate the data
import pandas as pd

#Get sqlalchemy to connect to the DB
from sqlalchemy import create_engine, text

#Get datetime to add a timestamp to the data
from datetime import datetime, timezone

#Specify Credentials
user = "{USERNAME}"
password = "{PASSWORD}"
host = "{HOST}"
database = "{DATABASE NAME}"

#Create the engine to populate the DB
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

#Load the CSV file
df = pd.read_csv("stocklevels.csv")

#Add timestamp column which is expected by DB
df["lastUpdatedDT"] = datetime.now(timezone.utc)

#Truncate the existing table before re-seeding to prevent duplicate rows
#on repeated runs. TRUNCATE is faster than DELETE and resets the auto-increment counter.
with engine.connect() as conn:
    conn.execute(text("TRUNCATE TABLE api_stocklevels"))
    conn.commit()
    print("Existing records cleared.")

#Perform the import
df.to_sql("api_stocklevels", con=engine, if_exists="append", index=False)

#Print the number of records imported
print(f"Imported {len(df)} records to the database.")

#Close the connection
engine.dispose()