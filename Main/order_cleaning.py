"""
order_cleaning.py

Module for validating, cleaning, and standardizing sales order records.

Pipeline Steps:
    1. Type Conversion: Converts identifiers, payment methods, dates, and quantities.
    2. Missing Value Check: Ensures required transactional fields are populated.
    3. Duplicate Removal: Removes duplicate records and duplicate Order_IDs.
    4. Referential Integrity: Verifies Customer_ID exists in Cleaned_Data/Customers.csv
       and Product_ID exists in Cleaned_Data/Products.csv.
    5. Order Date Validation: Verifies valid dates; rejects future dates.
    6. Quantity Validation: Ensures positive integer quantities (> 0).
    7. Payment Method & Status Validation: Normalizes and matches allowed domain values.
    8. Dataset Splitting: Partitions records into Cleaned_Data/Orders.csv and Rejected_Data/Rejected_Orders.csv.
"""

import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)


def convert_order_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts order columns to their respective data types.

    Args:
        df (pd.DataFrame): Raw order DataFrame.

    Returns:
        pd.DataFrame: DataFrame with typed columns.
    """
    logger.info("Converting Order Data Types...")
    string_columns = [
        "Order_ID",
        "Customer_ID",
        "Product_ID",
        "Payment_Method",
        "Order_Status",
    ]

    for column in string_columns:
        df[column] = df[column].astype("string")

    df["Order_Date"] = pd.to_datetime(df["Order_Date"],errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")

    logger.info("Order Data Types Converted Successfully.")
    return df


def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Checks for missing values across transactional fields.
    Leaves critical missing fields unpopulated for rejection routing.

    Args:
        df (pd.DataFrame): Order DataFrame.

    Returns:
        pd.DataFrame: Order DataFrame.
    """

    logger.info("Checking Missing Values in Order dataset...")

    missing_count = df.isna().sum().sum()

    logger.info("Total Missing Values Found: %d", missing_count)
    logger.info("Missing Values Checked Successfully.")

    return df
    


def clean_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes exact duplicate rows across all columns.
    """

    logger.info("Cleaning Duplicate Rows...")

    before = len(df)

    df = df.drop_duplicates()

    after = len(df)

    logger.info("Duplicate Rows Removed: %d", before - after)

    return df


def clean_duplicate_order_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects duplicate Order_IDs and flags them for rejection.

    Args:
        df (pd.DataFrame): Order DataFrame.

    Returns:
        pd.DataFrame: DataFrame with duplicate Order_IDs flagged.
    """

    logger.info("Checking Duplicate Order IDs...")

    df["Duplicate_Order_ID"] = df.duplicated(
        subset=["Order_ID"],
        keep="first"
    )

    logger.info(
        "Duplicate Order_IDs Found: %d",
        df["Duplicate_Order_ID"].sum()
    )

    return df


def clean_customer_reference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates referential integrity against Cleaned_Data/valid_data/Customers.csv.
    Flags invalid customer IDs as pd.NA.

    Args:
        df (pd.DataFrame): Order DataFrame.

    Returns:
        pd.DataFrame: DataFrame with verified Customer_IDs.
    """
    logger.info("Validating Customer References...")
    customers = pd.read_csv("Cleaned_Data/valid_data/Customers.csv", dtype={"Customer_ID": str})
    valid_customer_ids = set(customers["Customer_ID"])

    invalid_customer = ~df["Customer_ID"].isin(valid_customer_ids)
    logger.info("Invalid Customer_ID References Found: %d", invalid_customer.sum())

    df.loc[invalid_customer, "Customer_ID"] = pd.NA
    logger.info("Customer Reference Validation Completed.")
    return df


def clean_product_reference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates referential integrity against Cleaned_Data/valid_data/Products.csv.
    Flags invalid product IDs as pd.NA.

    Args:
        df (pd.DataFrame): Order DataFrame.

    Returns:
        pd.DataFrame: DataFrame with verified Product_IDs.
    """
    logger.info("Validating Product References...")
    products = pd.read_csv("Cleaned_Data/valid_data/Products.csv", dtype={"Product_ID": str})
    valid_product_ids = set(products["Product_ID"])

    invalid_product = ~df["Product_ID"].isin(valid_product_ids)
    logger.info("Invalid Product_ID References Found: %d", invalid_product.sum())

    df.loc[invalid_product, "Product_ID"] = pd.NA
    logger.info("Product Reference Validation Completed.")
    return df


def clean_order_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates order dates. Rejects unparseable or future order dates.

    Args:
        df (pd.DataFrame): Order DataFrame.

    Returns:
        pd.DataFrame: DataFrame with validated order dates.
    """
    logger.info("Cleaning Order Dates...")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    today = pd.Timestamp.today().normalize()

    future_dates = df["Order_Date"] > today
    logger.info("Future Dates Found: %d", future_dates.sum())
    df.loc[future_dates, "Order_Date"] = pd.NaT

    invalid_dates = df["Order_Date"].isna()
    logger.info("Invalid Dates Found: %d", invalid_dates.sum())
    logger.info("Order Date Cleaning Completed.")
    return df


def clean_quantity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates item quantities. Rejects non-numeric, zero, or negative quantities.

    Args:
        df (pd.DataFrame): Order DataFrame.

    Returns:
        pd.DataFrame: DataFrame with validated quantities.
    """
    logger.info("Cleaning Quantity...")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    invalid_quantity = df["Quantity"].isna() | (df["Quantity"] <= 0)

    logger.info("Invalid Quantities Found: %d", invalid_quantity.sum())
    df.loc[invalid_quantity, "Quantity"] = pd.NA
    logger.info("Quantity Cleaning Completed.")
    return df


def clean_payment_method(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trims, title-cases, and matches payment methods against allowed list:
    ['Upi', 'Credit Card', 'Debit Card', 'Net Banking', 'Cash On Delivery', 'Wallet'].

    Args:
        df (pd.DataFrame): Order DataFrame.

    Returns:
        pd.DataFrame: DataFrame with validated payment methods.
    """
    logger.info("Cleaning Payment Methods...")
    df["Payment_Method"] = df["Payment_Method"].str.strip().str.title()
    valid_methods = [
        "Upi",
        "Credit Card",
        "Debit Card",
        "Net Banking",
        "Cash On Delivery",
        "Wallet",
    ]

    invalid_payment = ~df["Payment_Method"].isin(valid_methods)
    logger.info("Invalid Payment Methods Found: %d", invalid_payment.sum())
    df.loc[invalid_payment, "Payment_Method"] = pd.NA
    logger.info("Payment Method Cleaning Completed.")
    return df


def clean_order_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trims, title-cases, and matches order statuses against allowed list:
    ['Completed', 'Pending', 'Cancelled', 'Returned'].

    Args:
        df (pd.DataFrame): Order DataFrame.

    Returns:
        pd.DataFrame: DataFrame with validated order statuses.
    """
    logger.info("Cleaning Order Status...")
    df["Order_Status"] = df["Order_Status"].str.strip().str.title()
    valid_status = ["Completed", "Pending", "Cancelled", "Returned"]

    invalid_status = ~df["Order_Status"].isin(valid_status)
    logger.info("Invalid Order Status Found: %d", invalid_status.sum())
    df.loc[invalid_status, "Order_Status"] = pd.NA
    logger.info("Order Status Cleaning Completed.")
    return df


def split_clean_and_rejected(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits orders into Cleaned and Rejected DataFrames with failure rationales.
    Exports to Cleaned_Data/Orders.csv and Rejected_Data/Rejected_Orders.csv.

    Args:
        df (pd.DataFrame): Processed order DataFrame.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (cleaned_df, rejected_df)
    """
    logger.info("Splitting Cleaned and Rejected Records...")
    df["Reject_Reason"] = pd.Series("", index=df.index, dtype="string")

    df.loc[df["Duplicate_Order_ID"], "Reject_Reason"] += "Duplicate Order_ID, "
    df.loc[df["Customer_ID"].isna(), "Reject_Reason"] += "Invalid Customer_ID, "
    df.loc[df["Product_ID"].isna(), "Reject_Reason"] += "Invalid Product_ID, "
    df.loc[df["Order_Date"].isna(), "Reject_Reason"] += "Invalid Order Date, "
    df.loc[df["Quantity"].isna(), "Reject_Reason"] += "Invalid Quantity, "
    df.loc[df["Payment_Method"].isna(), "Reject_Reason"] += "Invalid Payment Method, "
    df.loc[df["Order_Status"].isna(), "Reject_Reason"] += "Invalid Order Status, "

    df["Reject_Reason"] = df["Reject_Reason"].str.rstrip(", ")

    rejected_condition = df["Reject_Reason"] != ""
    rejected_df = df[rejected_condition].copy()
    cleaned_df = df[~rejected_condition].copy()

    # Remove Reject_Reason from cleaned data
    cleaned_df = cleaned_df.drop(
    columns=["Reject_Reason", "Duplicate_Order_ID"]
    )

    rejected_df = rejected_df.drop(
        columns=["Duplicate_Order_ID"]
    )

    os.makedirs("Cleaned_Data", exist_ok=True)
    os.makedirs("Rejected_Data", exist_ok=True)
    cleaned_df["Created_at"] = pd.Timestamp.now()

    cleaned_df.to_csv("Cleaned_Data/valid_data/Orders.csv", index=False)
    rejected_df.to_csv("Cleaned_Data/Rejected_Data/Rejected_Orders.csv", index=False)

    logger.info(
        "Cleaning Summary: Total=%d, Clean=%d, Rejected=%d",
        len(df),
        len(cleaned_df),
        len(rejected_df),
    )
    if not rejected_df.empty:
        logger.info(
            "Sample Rejected Orders:\n%s",
            rejected_df[["Order_ID", "Reject_Reason"]].head(10).to_string(index=False),
        )
    logger.info("Orders.csv and Rejected_Orders.csv Saved Successfully.")
    return cleaned_df, rejected_df


def clean_orders(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Executes the entire order data cleaning pipeline.

    Args:
        df (pd.DataFrame): Raw order DataFrame.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Tuple of (cleaned_df, rejected_df).
    """
    logger.info("=" * 60)
    logger.info("ORDER CLEANING PIPELINE STARTED")
    logger.info("=" * 60)

    df = convert_order_types(df)
    df = clean_missing_values(df)
    df = clean_duplicate_rows(df)
    df = clean_duplicate_order_ids(df)
    df = clean_customer_reference(df)
    df = clean_product_reference(df)
    df = clean_order_date(df)
    df = clean_quantity(df)
    df = clean_payment_method(df)
    df = clean_order_status(df)

    cleaned_df, rejected_df = split_clean_and_rejected(df)

    logger.info("=" * 60)
    logger.info("ORDER CLEANING PIPELINE COMPLETED")
    logger.info("=" * 60)
    return cleaned_df, rejected_df