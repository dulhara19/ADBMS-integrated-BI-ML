from mlxtend.frequent_patterns import apriori, association_rules
# from mlxtend.frequent_patterns import fpgrowth  # Uncomment to try FP-Growth
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

# Filter items purchased in at least 5 transactions
min_transactions = 5
basket = basket.loc[:, basket.sum() >= min_transactions]

# Debug: Print dataset size
print("Transactions:", basket.shape[0])
print("Unique items (after filtering):", basket.shape[1])

if basket.shape[1] == 0:
    print(f"No items appear in at least {min_transactions} transactions. Try lowering threshold.")
else:
    # Use apriori with higher min_support and max_len to limit computation
    frequent_itemsets = apriori(basket, min_support=0.03, use_colnames=True, max_len=3)
    
    # Or use FP-Growth instead for faster performance (uncomment below)
    # frequent_itemsets = fpgrowth(basket, min_support=0.03, use_colnames=True, max_len=3)

    if not frequent_itemsets.empty:
        print("Frequent itemsets found:", len(frequent_itemsets))
        
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)
        
        print("\nTop 10 association rules sorted by lift:")
        print(rules.sort_values(by="lift", ascending=False).head(10))
    else:
        print("⚠️ No frequent itemsets found. Try lowering min_support or reducing item filtering.")

#lets plot now
import matplotlib.pyplot as plt
import networkx as nx

plt.figure(figsize=(8,6))
plt.scatter(rules['support'], rules['confidence'], alpha=0.6, edgecolors='r')
plt.xlabel('Support')
plt.ylabel('Confidence')
plt.title('Support vs Confidence for Association Rules')
plt.grid(True)
plt.show()
# Create a network graph of the top association rules
# Select top N rules by lift for clarity
top_rules = rules.sort_values('lift', ascending=False).head(20)

G = nx.DiGraph()

# Add edges for each rule
for _, row in top_rules.iterrows():
    for antecedent in row['antecedents']:
        for consequent in row['consequents']:
            G.add_edge(antecedent, consequent, weight=row['lift'])

plt.figure(figsize=(12,8))
pos = nx.spring_layout(G, k=0.5, iterations=20)
edges = G.edges(data=True)

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightblue')
# Draw edges
nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, edge_color='gray')
# Draw labels
nx.draw_networkx_labels(G, pos, font_size=10)

plt.title('Top Association Rules Network Graph')
plt.axis('off')
plt.show()