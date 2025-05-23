from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd
from connector import get_connection

conn = get_connection()

query = "SELECT InvoiceNo, Description, Quantity FROM onlineretail"
df = pd.read_sql(query, conn)
conn.close()

# Clean Description and InvoiceNo
df['Description'] = df['Description'].astype(str).str.strip()
df['InvoiceNo'] = df['InvoiceNo'].astype(str)

# Filter only positive quantities
df = df[df['Quantity'] > 0]

# Create basket (InvoiceNo as rows, items as columns)
basket = df.groupby(['InvoiceNo', 'Description'])['Quantity'].sum().unstack().fillna(0)

# Convert all values to 1 or 0 (binary encoding)
basket = basket.applymap(lambda x: 1 if x > 0 else 0)

# Ensure all values are integers
basket = basket.astype('int')

# Convert basket to True/False for better memory efficiency
basket = basket > 0
basket = basket.astype(bool)

# Optional: filter out rarely purchased items (less than 50 transactions, for example)
basket = basket.loc[:, basket.sum() > 50]

# Now apply Apriori
frequent_itemsets = apriori(basket, min_support=0.05, use_colnames=True)

# Generate rules
rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

# Show top rules
print(rules.sort_values(by="lift", ascending=False).head(10))

print("Transactions:", basket.shape[0])
print("Unique items:", basket.shape[1])


# # Clean data
# df.dropna(inplace=True)
# df = df[df['Quantity'] > 0]
# df['Description'] = df['Description'].str.strip()


# # Run Apriori
# frequent_itemsets = apriori(basket, min_support=0.01, use_colnames=True)
# rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

# #debugging
# print(basket.dtypes.value_counts())
# print(basket.head())


# # Show rules
# top_rules = rules.sort_values(by='lift', ascending=False).head(10)
# print(top_rules)
