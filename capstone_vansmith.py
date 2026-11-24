"""
ISM2411 Capstone — Retail Store Sales Analysis
Author: Van Smith
Date:   [Submission Date]

Business Questions:
  1. Which category drives the most revenue, and is it the same in every region?
  2. Which categories get returned most, and what do returns cost?
  3. Do Corporate customers place bigger orders than Consumers?

AI Disclosure: AI was used to look up Pandas and Matplotlib syntax for business questions. All interpretations and written reports were done by myself with no AI assistance.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ── 1. LOAD ───────────────────────────────────────────────────
DATA_FILE = "data/capstone_retail.csv"   # ← your dataset's file
df = pd.read_csv(DATA_FILE)
print("Raw shape:", df.shape)
print(df.head())
df.info()
print(df.isnull().sum())

# ── 2. CLEAN ──────────────────────────────────────────────────
# Document every decision with a comment explaining WHY.

# Standardize column names
df.columns = df.columns.str.lower().str.replace(" ", "_")

# Drop rows missing essential identifiers
# Reason: cannot attribute revenue without an order date
df = df.dropna(subset=["order_date"])

# Parse order_date — coerce bad dates to NaT
df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

# Fix unit_price: strip "$" and ",", convert to float
df["unit_price"] = df["unit_price"].str.replace("$", "", regex=False)
df["unit_price"] = df["unit_price"].str.replace(",", "", regex=False).astype(float)

# Exclude returns (negative unit_price)
# Reason: question focuses on forward sales; returns analyzed separately
df = df[df["unit_price"] >= 0]

# Remove impossible values that describe() reveals
# Reason: a quantity of 9999 is a placeholder someone typed, not a real order
df = df[df["quantity_sold"] != 9999]

# Fill missing quantity_sold with median (low %, aggregate impact minimal)
df["quantity_sold"] = df["quantity_sold"].fillna(df["quantity_sold"].median())

# Fix category typos: case and spaces first, then the misspellings
# that value_counts() shows
df["product_category"] = df["product_category"].str.strip().str.title()
df["product_category"] = df["product_category"].replace(
    {"Electronix": "Electronics", "Furnitu Re": "Furniture"}
)

# Remove duplicates
df = df.drop_duplicates()
print("Clean shape:", df.shape)

# ── 3. DERIVED COLUMNS ────────────────────────────────────────
df["revenue"] = df["unit_price"] * df["quantity_sold"]
df["month"] = df["order_date"].dt.month
df["quarter"] = df["order_date"].dt.quarter

# ── 4. DESCRIPTIVE SUMMARY ───────────────────────────────────
print("\nDescriptive stats (clean):")
print(df.describe())
print("\nRevenue by region:")
print(df.groupby("region")["revenue"].sum().sort_values(ascending=False))

# ── 5. BUSINESS QUESTION 1 ────────────────────────────────────
# Which category drives the most revenue, and is it the same in every region?

# Analysis code
print("\nRevenue by category in each region")
print(df.groupby(["region", "product_category"])["revenue"].sum().sort_values(ascending=False))
revenue_by_category_and_region = df.groupby(["region", "product_category"])["revenue"].sum().sort_values(ascending=False)
# Chart code
revenue_pivot = df.pivot_table(
    index="product_category",
    columns="region",
    values="revenue",
    aggfunc="sum",
    fill_value=0,
)
revenue_pivot = revenue_pivot.loc[revenue_pivot.sum(axis=1).sort_values().index]

fig, ax = plt.subplots(figsize=(9, 5))
sns.heatmap(
    revenue_pivot,
    annot=True,
    fmt=",.0f",
    cmap="Blues",
    linewidths=0.5,
    cbar_kws={"label": "Revenue ($)"},
    ax=ax,
)
ax.set(title="Revenue by Category and Region", xlabel="Region", ylabel="Category")
plt.tight_layout()
plt.savefig("charts/revenue_by_category_and_region.png", dpi=150, bbox_inches="tight")
plt.show()
# The category that drives the most revenue is electronics, which applies for every region in the dataset.

# ── 6. BUSINESS QUESTION 2 ────────────────────────────────────
# Which categories get returned most, and what do returns cost?
# [Analysis + chart]

# ── 7. BUSINESS QUESTION 3 ────────────────────────────────────
# Do Corporate customers place bigger orders than Consumers?
# [Analysis + chart]

# ── 8. SAVE CLEAN DATA ────────────────────────────────────────
df.to_csv("data/clean_data.csv", index=False)
print("\nCapstone complete. Clean data saved to data/clean_data.csv")