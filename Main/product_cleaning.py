"""
product_cleaning.py

Module for validating, cleaning, and standardizing product catalog records.

Pipeline Steps:
    1. Type Conversion: Converts textual columns to string and Price to numeric.
    2. Missing Value Handling: Fills missing Product_Name with 'Unknown'.
    3. Duplicate Removal: Drops exact duplicate records and duplicate Product_IDs.
    4. Text Standardization: Cleans and title-cases Product_Name, Category, Sub_Category, and Supplier.
    5. Price Validation: Ensures positive numeric prices; flags zero or negative prices as invalid.
    6. Dataset Splitting: Partitions records into Cleaned_Data/Products.csv and Rejected_Data/Rejected_Products.csv.
"""

import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)


def convert_product_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts product columns to appropriate data types.

    Args:
        df (pd.DataFrame): Raw product DataFrame.

    Returns:
        pd.DataFrame: DataFrame with standardized column types.
    """
    logger.info("Converting Product Data Types...")
    string_columns = [
        "Product_ID",
        "Product_Name",
        "Category",
        "Sub_Category",
        "Supplier",
    ]

    for column in string_columns:
        df[column] = df[column].astype("string")

    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    logger.info("Product Data Types Converted Successfully.")
    return df


def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Imputes missing product names with 'Unknown'.
    Other missing columns are left as NA to allow rejection classification.

    Args:
        df (pd.DataFrame): Product DataFrame.

    Returns:
        pd.DataFrame: DataFrame with imputed product names.
    """
    logger.info("Cleaning Missing Values...")
    df["Product_Name"] = df["Product_Name"].fillna("Unknown")
    logger.info("Missing Values Cleaned Successfully.")
    return df


def clean_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes fully duplicated product rows.

    Args:
        df (pd.DataFrame): Product DataFrame.

    Returns:
        pd.DataFrame: Deduplicated DataFrame.
    """
    logger.info("Cleaning Duplicate Rows...")
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    logger.info("Duplicate Rows Removed: %d", before - after)
    return df


def clean_duplicate_product_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects duplicate Product_IDs and flags them for rejection.

    Args:
        df (pd.DataFrame): Product DataFrame.

    Returns:
        pd.DataFrame: DataFrame with duplicate Product_IDs flagged.
    """
    logger.info("Checking Duplicate Product IDs...")

    df["Duplicate_Product_ID"] = df.duplicated(
        subset=["Product_ID"],
        keep="first"
    )

    logger.info(
        "Duplicate Product_IDs Found: %d",
        df["Duplicate_Product_ID"].sum()
    )

    return df


def clean_product_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trims and title-cases product names. Converts empty strings to pd.NA.

    Args:
        df (pd.DataFrame): Product DataFrame.

    Returns:
        pd.DataFrame: Standardized product DataFrame.
    """
    logger.info("Cleaning Product Names...")
    df["Product_Name"] = df["Product_Name"].str.strip().str.title()
    df.loc[df["Product_Name"] == "", "Product_Name"] = pd.NA

    missing_count = df["Product_Name"].isna().sum()
    logger.info("Missing Product Names Found: %d", missing_count)
    logger.info("Product Name Cleaning Completed.")
    return df


def clean_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trims and title-cases categories. Converts empty strings to pd.NA.

    Args:
        df (pd.DataFrame): Product DataFrame.

    Returns:
        pd.DataFrame: Standardized product DataFrame.
    """
    logger.info("Cleaning Product Categories...")
    df["Category"] = df["Category"].str.strip().str.title()
    df.loc[df["Category"] == "", "Category"] = pd.NA

    missing_count = df["Category"].isna().sum()
    logger.info("Missing Categories Found: %d", missing_count)
    logger.info("Product Category Cleaning Completed.")
    return df


def clean_sub_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trims and title-cases sub-categories.
    Replaces missing values with 'Unknown'.
    """

    logger.info("Cleaning Product Sub-Categories...")

    df["Sub_Category"] = df["Sub_Category"].str.strip().str.title()

    df["Sub_Category"] = df["Sub_Category"].replace("", pd.NA)

    df["Sub_Category"] = df["Sub_Category"].fillna("Unknown")

    missing_count = (df["Sub_Category"] == "Unknown").sum()

    logger.info("Missing Sub-Categories Found: %d", missing_count)

    logger.info("Product Sub-Category Cleaning Completed.")

    return df


def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates product price. Flags non-numeric, zero, or negative prices as pd.NA.

    Args:
        df (pd.DataFrame): Product DataFrame.

    Returns:
        pd.DataFrame: DataFrame with validated prices.
    """
    logger.info("Cleaning Product Prices...")
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    invalid_price = df["Price"].isna() | (df["Price"] <= 0)

    logger.info("Invalid Prices Found: %d", invalid_price.sum())
    df.loc[invalid_price, "Price"] = pd.NA
    logger.info("Product Price Cleaning Completed.")
    return df


def clean_supplier(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trims and title-cases supplier names. Converts empty strings to pd.NA.

    Args:
        df (pd.DataFrame): Product DataFrame.

    Returns:
        pd.DataFrame: Standardized product DataFrame.
    """
    logger.info("Cleaning Supplier Names...")

    df["Supplier"] = df["Supplier"].str.strip().str.title()

    df["Supplier"] = df["Supplier"].replace("", pd.NA)
    df["Supplier"] = df["Supplier"].fillna("Unknown")

    missing_count = (df["Supplier"] == "Unknown").sum()

    logger.info("Missing Suppliers Found: %d", missing_count)
    logger.info("Supplier Cleaning Completed.")

    return df


def split_clean_and_rejected(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits products into Cleaned and Rejected DataFrames with rejection reasons.
    Exports to Cleaned_Data/Products.csv and Rejected_Data/Rejected_Products.csv.

    Args:
        df (pd.DataFrame): Processed product DataFrame.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (cleaned_df, rejected_df)
    """
    logger.info("Splitting Cleaned and Rejected Records...")
    df["Reject_Reason"] = pd.Series("", index=df.index, dtype="string")

    df.loc[df["Category"].isna(), "Reject_Reason"] += "Missing Category, "

    df.loc[df["Price"].isna(), "Reject_Reason"] += "Invalid Price, "

    df.loc[df["Duplicate_Product_ID"], "Reject_Reason"] += "Duplicate Product_ID, " 

    df["Reject_Reason"] = df["Reject_Reason"].str.rstrip(", ")

    rejected_condition = df["Reject_Reason"] != ""
    rejected_df = df[rejected_condition].copy()
    cleaned_df = df[~rejected_condition].copy()

    # Remove Reject_Reason from cleaned data
    cleaned_df = cleaned_df.drop(
    columns=["Reject_Reason", "Duplicate_Product_ID"])

    rejected_df = rejected_df.drop(
    columns=["Duplicate_Product_ID"])

    os.makedirs("Cleaned_Data", exist_ok=True)
    os.makedirs("Rejected_Data", exist_ok=True)
    cleaned_df["Created_at"] = pd.Timestamp.now()

    cleaned_df.to_csv("Cleaned_Data/valid_data/Products.csv", index=False)
    rejected_df.to_csv("Cleaned_Data/Rejected_Data/Rejected_Products.csv", index=False)

    logger.info(
        "Cleaning Summary: Total=%d, Clean=%d, Rejected=%d",
        len(df),
        len(cleaned_df),
        len(rejected_df),
    )
    if not rejected_df.empty:
        logger.info(
            "Sample Rejected Products:\n%s",
            rejected_df[["Product_ID", "Reject_Reason"]].head(10).to_string(index=False),
        )

    logger.info("Products.csv and Rejected_Products.csv Saved Successfully.")
    return cleaned_df, rejected_df


def clean_products(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Executes the entire product data cleaning pipeline.

    Args:
        df (pd.DataFrame): Raw product DataFrame.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Tuple of (cleaned_df, rejected_df).
    """
    logger.info("=" * 60)
    logger.info("PRODUCT CLEANING PIPELINE STARTED")
    logger.info("=" * 60)

    df = convert_product_types(df)
    df = clean_missing_values(df)
    df = clean_duplicate_rows(df)
    df = clean_duplicate_product_ids(df)
    df = clean_product_name(df)
    df = clean_category(df)
    df = clean_sub_category(df)
    df = clean_price(df)
    df = clean_supplier(df)

    cleaned_df, rejected_df = split_clean_and_rejected(df)

    logger.info("=" * 60)
    logger.info("PRODUCT CLEANING PIPELINE COMPLETED")
    logger.info("=" * 60)

    return cleaned_df, rejected_df