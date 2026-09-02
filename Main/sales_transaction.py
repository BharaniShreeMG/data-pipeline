"""
sales_transaction.py

Creates the final Sales_Transaction dataset from the cleaned
Customers, Products and Orders datasets.

Business Rule:
    Only Completed orders contribute to revenue.

Output:
    Cleaned_Data/valid_data/Sales_Transaction.csv
"""

import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)


def create_sales_transaction_df():
    """
    Creates the Sales_Transaction DataFrame
    and exports it as CSV.

    Returns
    -------
    pd.DataFrame
    """

    logger.info("=" * 60)
    logger.info("CREATING SALES_TRANSACTION DATASET")
    logger.info("=" * 60)

    customers = pd.read_csv("Cleaned_Data/valid_data/Customers.csv")
    products = pd.read_csv("Cleaned_Data/valid_data/Products.csv")
    orders = pd.read_csv("Cleaned_Data/valid_data/Orders.csv")

    logger.info("Merging Orders and Customers...")

    sales = orders.merge(
        customers,
        on="Customer_ID",
        how="inner"
    )

    logger.info("Merging Products...")

    sales = sales.merge(
        products,
        on="Product_ID",
        how="inner"
    )

    logger.info("Creating Derived Columns...")

    sales["Total_Amount"] = (
        sales["Quantity"] * sales["Price"]
    ).where(
        sales["Order_Status"] == "Completed",
        0
    )

    sales["Order_Date"] = pd.to_datetime(
        sales["Order_Date"]
    )

    sales["Order_Year"] = sales["Order_Date"].dt.year

    sales["Order_Month"] = (
        sales["Order_Date"]
        .dt.month_name()
    )

    sales["YearMonth"] = sales["Order_Date"].dt.strftime("%Y-%m")
    sales["Created_at"] = pd.Timestamp.now()


    sales = sales[
        [
            "Order_ID",
            "Order_Date",
            "Customer_ID",
            "Customer_Name",
            "City",
            "State",
            "Product_ID",
            "Product_Name",
            "Category",
            "Sub_Category",
            "Quantity",
            "Price",
            "Total_Amount",
            "Payment_Method",
            "Order_Status",
            "Order_Year",
            "Order_Month",
            "YearMonth",
            "Created_at"
        ]
    ]

    output_dir = os.path.join(
        "Cleaned_Data",
        "valid_data"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    output_file = os.path.join(
        output_dir,
        "Sales_Transaction.csv"
    )

    sales.to_csv(
        output_file,
        index=False
    )

    logger.info(
        "Sales_Transaction.csv created successfully."
    )

    logger.info(
        "Total Records : %s",
        f"{len(sales):,}"
    )

    logger.info(
        "Output File   : %s",
        output_file
    )

    logger.info("=" * 60)

    return sales


if __name__ == "__main__":
    create_sales_transaction_df()