import pandas as pd
from connector import get_connection

# Load the CSV
df = pd.read_csv("csvdata.csv")
df.columns = df.columns.str.strip()
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
df = df.dropna(subset=['InvoiceDate'])
df.fillna('', inplace=True)

conn = get_connection()
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

conn.commit()
cursor.close()
conn.close()
print("✅ Data inserted successfully.")
