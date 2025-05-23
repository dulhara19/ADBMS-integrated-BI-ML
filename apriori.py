from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd
from connector import get_connection

# Connect to database and load data
conn = get_connection()
query = "SELECT InvoiceNo, Description, Quantity FROM onlineretail"
df = pd.read_sql(query, conn)
conn.close()

# Clean data
df['Description'] = df['Description'].astype(str).str.strip()
df['InvoiceNo'] = df['InvoiceNo'].astype(str)
df = df[df['Quantity'] > 0]

# Create basket format
basket = df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0)

# Convert quantities to booleans (True if >0)
basket = basket > 0

# Filter items purchased in at least 30 transactions
basket = basket.loc[:, basket.sum() > 30]

# Debug: Print dataset size
print("Transactions:", basket.shape[0])
print("Unique items (after filtering):", basket.shape[1])

# Run Apriori
frequent_itemsets = apriori(basket, min_support=0.01, use_colnames=True)

if not frequent_itemsets.empty:
    print("Frequent itemsets found:", len(frequent_itemsets))

    # Generate rules
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
    
    # Print top rules
    print("\nTop 10 association rules sorted by lift:")
    print(rules.sort_values(by="lift", ascending=False).head(10))
else:
    print("⚠️ No frequent itemsets found. Try lowering `min_support` or reducing item filtering.")
