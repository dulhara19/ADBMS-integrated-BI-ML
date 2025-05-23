import pandas as pd
import mysql.connector
from dotenv import load_dotenv
import os
from mlxtend.frequent_patterns import apriori, association_rules

load_dotenv()  # load variables from .env file

# Load the CSV file
df = pd.read_csv("csvdata.csv")

# Clean column names (optional but good practice)
df.columns = df.columns.str.strip()

# Convert InvoiceDate to datetime safely
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')

# Drop rows where date conversion failed (optional)
df = df.dropna(subset=['InvoiceDate'])

# Fill other missing values
df.fillna('', inplace=True)

# Connect to MySQL
conn = mysql.connector.connect(
  host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME') 
)
cursor = conn.cursor()

# Insert rows
for index, row in df.iterrows():
    try:
        sql = """
        INSERT INTO onlineretail (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = (
            str(row['InvoiceNo']),
            str(row['StockCode']),
            str(row['Description']),
            int(row['Quantity']),
            row['InvoiceDate'].strftime('%Y-%m-%d %H:%M:%S'),
            float(row['UnitPrice']),
            str(row['CustomerID']) if row['CustomerID'] != '' else None,
            str(row['Country'])
        )
        cursor.execute(sql, data)
    except Exception as e:
        print(f"Error on row {index}: {e}")

# Finalize
conn.commit()
cursor.close()
conn.close()
print("✅ Data inserted successfully.")
