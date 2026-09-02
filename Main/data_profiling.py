"""
data_profiling.py

Displays data quality issues present in the raw datasets.
"""

import pandas as pd
import logging
logger= logging.getLogger(__name__)

# ---------------- CUSTOMER PROFILE ---------------- #

def profile_customers():

    df = pd.read_csv("Raw_Data/customers.csv")

    email_pattern = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"

    phone = (
        df["Phone"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.replace(r"\D", "", regex=True)
    )

    registration_date = pd.to_datetime(
        df["Registration_Date"],
        errors="coerce"
    )

    logger.info("\n" + "=" * 60)
    logger.info("CUSTOMER DATA PROFILE")
    logger.info("=" * 60)

    logger.info("Total Records: %d", len(df))
    logger.info("Missing Phone: %d", df["Phone"].isna().sum())
    logger.info("Invalid Phone: %d", (phone.str.len() != 10).sum())
    email = df["Email"].fillna("").str.strip().str.lower()
    logger.info("Missing Email: %d", df["Email"].isna().sum())
    logger.info("Invalid Email: %d", (~email.str.match(email_pattern)).sum())
    logger.info("Duplicate Customer_ID: %d", df.duplicated(subset=["Customer_ID"]).sum())
    logger.info("Duplicate Record: %d", df.duplicated().sum())
    logger.info("Invalid Registration Date: %d", registration_date.isna().sum())
    logger.info("Missing City: %d", df["City"].isna().sum())
    logger.info("Missing State: %d", df["State"].isna().sum())
    logger.info(
        "Inconsistent City: %d",
        (
            df["City"].fillna("")
            != df["City"].fillna("").str.strip().str.title()
        ).sum()
    )


# ---------------- PRODUCT PROFILE ---------------- #

def profile_products():

    df = pd.read_csv("Raw_Data/products.csv")

    price = pd.to_numeric(
        df["Price"],
        errors="coerce"
    )

    logger.info("\n" + "=" * 60)
    logger.info("PRODUCT DATA PROFILE")
    logger.info("=" * 60)

    logger.info("Total Records: %d", len(df))
    logger.info("Missing Product Name: %d", df["Product_Name"].isna().sum())
    logger.info("Missing Supplier: %d", df["Supplier"].isna().sum())
    logger.info("Negative Price: %d", (price < 0).sum())
    logger.info("Zero Price: %d", (price == 0).sum())
    logger.info("Duplicate Product_ID: %d", df.duplicated(subset=["Product_ID"]).sum())
    logger.info("Duplicate Record: %d", df.duplicated().sum())
    logger.info("Missing Category: %d", df["Category"].isna().sum())
    logger.info("Missing Sub Category: %d", df["Sub_Category"].isna().sum())
    logger.info(
        "Inconsistent Category: %d",
        (
            df["Category"].fillna("")
            != df["Category"].fillna("").str.strip().str.title()
        ).sum()
)
# ---------------- ORDER PROFILE ---------------- #

def profile_orders():

    df = pd.read_csv("Raw_Data/orders.csv")

    quantity = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    order_date = pd.to_datetime(
        df["Order_Date"],
        errors="coerce"
    )
    customer_pattern = r"^CUST\d{5}$"
    product_pattern = r"^PROD\d{5}$"

    logger.info("\n" + "=" * 60)
    logger.info("ORDER DATA PROFILE")
    logger.info("=" * 60)

    logger.info("Total Records: %d", len(df))
    logger.info("Missing Payment Method: %d", df["Payment_Method"].isna().sum())
    logger.info("Missing Order Status: %d", df["Order_Status"].isna().sum())
    logger.info("Negative Quantity: %d", (quantity < 0).sum())
    logger.info("Zero Quantity: %d", (quantity == 0).sum())
    logger.info("Duplicate Order_ID: %d", df.duplicated(subset=["Order_ID"]).sum())
    logger.info("Duplicate Record: %d", df.duplicated().sum())
    logger.info(
        "Invalid Customer_ID: %d",
        (~df["Customer_ID"].astype(str).str.match(customer_pattern)).sum()
    )
    logger.info(
        "Invalid Product_ID: %d",
        (~df["Product_ID"].astype(str).str.match(product_pattern)).sum()
    )
    logger.info("Invalid Order Date: %d", order_date.isna().sum())
    logger.info("Future Order Date: %d", (order_date > pd.Timestamp.today()).sum())
    print("  ")

# ---------------- MAIN ---------------- #

def run_data_profile():

    profile_customers()
    profile_products()
    profile_orders()


if __name__ == "__main__":

    run_data_profile()