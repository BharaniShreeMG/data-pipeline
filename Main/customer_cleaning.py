"""
customer_cleaning.py

Module for validating, cleaning, and standardizing customer records.

Pipeline Steps:
    1. Type Conversion: Converts columns to string/datetime types.
    2. Missing Value Imputation: Fills acceptable missing fields with defaults.
    3. Duplicate Removal: Removes identical rows and flags duplicate Customer_IDs for rejection.
    4. Email Validation: Regex validation and lowercase standardization.
    5. Phone Validation: Digit extraction and length check (10 digits).
    6. Registration Date Validation: Converts to datetime, filters out future dates.
    7. Gender Standardization: Capitalizes and filters valid gender categories.
    8. City & State Standardization: Title cases and trims whitespace.
    9. Dataset Splitting: Partitions records into Cleaned and Rejected CSVs.
"""

import logging
import os
import re
import pandas as pd

logger = logging.getLogger(__name__)


def convert_customer_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts customer columns to their appropriate data types.

    Args:
        df (pd.DataFrame): Raw customer DataFrame.

    Returns:
        pd.DataFrame: DataFrame with standardized column types.
    """
    logger.info("Converting Customer Data Types...")
    string_columns = [
        "Customer_ID",
        "Customer_Name",
        "Email",
        "Phone",
        "Gender",
        "City",
        "State",
    ]

    for column in string_columns:
        df[column] = df[column].astype("string")

    df["Registration_Date"] = pd.to_datetime(
        df["Registration_Date"],
        errors="coerce"
    )
    logger.info("Customer Data Types Converted Successfully.")
    return df

def clean_customer_id(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates Customer_ID format.
    Only invalid Customer_IDs will be rejected.
    """

    logger.info("Validating Customer_ID...")

    customer_pattern = r"^CUST\d{5}$"

    invalid_customer = ~df["Customer_ID"].str.match(customer_pattern, na=False)

    logger.info("Invalid Customer_IDs Found: %d", invalid_customer.sum())

    df.loc[invalid_customer, "Customer_ID"] = pd.NA

    return df


def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Imputes missing values with standard default placeholders.

    Args:
        df (pd.DataFrame): Customer DataFrame.

    Returns:
        pd.DataFrame: Customer DataFrame with imputed defaults.
    """
    logger.info("Cleaning Missing Values...")
    df["Customer_Name"] = df["Customer_Name"].fillna("Unknown")
    df["Email"] = df["Email"].fillna("missingemail")
    df["Phone"] = df["Phone"].fillna("0000000000")
    df["Gender"] = df["Gender"].fillna("Unknown")
    df["City"] = df["City"].fillna("Unknown")
    df["State"] = df["State"].fillna("Unknown")
    logger.info("Missing Values Cleaned Successfully.")
    return df


def clean_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Removes exact duplicate rows across all columns.

    Args:
        df (pd.DataFrame): Customer DataFrame.

    Returns:
        pd.DataFrame: Deduplicated DataFrame.
    """
    logger.info("Cleaning Duplicate Rows...")
    before = len(df)
    df = df.drop_duplicates()
    after = len(df)
    logger.info("Duplicate Rows Removed: %d", before - after)
    return df


def clean_duplicate_customer_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detects duplicate Customer_IDs and marks them for rejection.
    Args:
        df (pd.DataFrame): Customer DataFrame.

    Returns:
        pd.DataFrame: DataFrame with unique Customer_IDs.
    """
    df["Duplicate_Customer_ID"] = df.duplicated(
        subset=["Customer_ID"],
        keep="first"
    )

    logger.info(
        "Duplicate Customer_IDs Found: %d",
        df["Duplicate_Customer_ID"].sum()
    )

    return df


def clean_email(df: pd.DataFrame) -> pd.DataFrame:
    """
    Trims, lowercases, and validates customer emails against RFC regex.
    Sets invalid emails to pd.NA for rejection routing.

    Args:
        df (pd.DataFrame): Customer DataFrame.

    Returns:
        pd.DataFrame: DataFrame with validated emails.
    """
    logger.info("Cleaning Email Addresses...")
    df["Email"] = df["Email"].str.strip().str.lower()
    df["Email"] = df["Email"].str.replace(" ", "", regex=False)

    email_pattern = r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
    invalid_email = ~df["Email"].str.match(email_pattern, na=False)
    logger.info("Invalid Emails Found: %d", invalid_email.sum())

    df.loc[invalid_email, "Email"] = pd.NA
    logger.info("Email Cleaning Completed.")
    return df


def clean_phone(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans phone numbers by extracting digits and verifying 10-digit length.
    Sets invalid numbers to pd.NA for rejection routing.

    Args:
        df (pd.DataFrame): Customer DataFrame.

    Returns:
        pd.DataFrame: DataFrame with validated phone numbers.
    """
    logger.info("Cleaning Phone Numbers...")
    df["Phone"] = df["Phone"].astype(str)
    df["Phone"] = df["Phone"].str.replace(".0", "", regex=False)
    df["Phone"] = df["Phone"].str.strip()
    df["Phone"] = df["Phone"].str.replace(r"\D", "", regex=True)

    invalid_phone = ((df["Phone"].str.len() != 10))
    logger.info("Invalid Phone Numbers Found: %d", invalid_phone.sum())

    df.loc[invalid_phone, "Phone"] = pd.NA
    return df


def clean_registration_date(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates registration dates and flags future or unparseable dates.

    Args:
        df (pd.DataFrame): Customer DataFrame.

    Returns:
        pd.DataFrame: DataFrame with validated registration dates.
    """
    logger.info("Cleaning Registration Dates...")
    df["Registration_Date"] = pd.to_datetime(
        df["Registration_Date"],
        errors="coerce"
    )
    today = pd.Timestamp.today().normalize()
    future_dates = df["Registration_Date"] > today
    logger.info("Future Dates Found: %d", future_dates.sum())

    df.loc[future_dates, "Registration_Date"] = pd.NaT
    invalid_dates = df["Registration_Date"].isna()
    logger.info("Invalid Dates Found: %d", invalid_dates.sum())
    logger.info("Registration Date Cleaning Completed.")
    return df


def clean_state(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes state names to Title Case and removes excess whitespace.

    Args:
        df (pd.DataFrame): Customer DataFrame.

    Returns:
        pd.DataFrame: DataFrame with standardized state names.
    """
    logger.info("Cleaning State Names...")
    df["State"] = df["State"].str.strip().str.title()
    logger.info("State Names Standardized Successfully.")
    return df


def clean_city(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes city names to Title Case and removes excess whitespace.

    Args:
        df (pd.DataFrame): Customer DataFrame.

    Returns:
        pd.DataFrame: DataFrame with standardized city names.
    """
    logger.info("Cleaning City Names...")
    df["City"] = df["City"].str.strip().str.title()
    logger.info("City Names Standardized Successfully.")
    return df


def clean_gender(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes gender values against allowed categories: ['Male', 'Female', 'Other'].
    Flags non-compliant entries as pd.NA.

    Args:
        df (pd.DataFrame): Customer DataFrame.

    Returns:
        pd.DataFrame: DataFrame with sanitized gender values.
    """
    logger.info("Cleaning Gender...")
    df["Gender"] = df["Gender"].str.strip().str.title()
    valid_gender = ["Male", "Female", "Other"]

    invalid_gender = ~df["Gender"].isin(valid_gender)
    logger.info("Invalid Genders Found: %d", invalid_gender.sum())

    df.loc[invalid_gender, "Gender"] = pd.NA
    logger.info("Gender Cleaning Completed.")
    return df


def split_clean_and_rejected(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits the customer records into Cleaned and Rejected DataFrames.
    Appends rejection reasons to failed records and saves both CSV files.

    Args:
        df (pd.DataFrame): Fully cleaned and tagged customer DataFrame.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: (cleaned_df, rejected_df)
    """
    logger.info("Splitting Cleaned and Rejected Records...")
    df["Reject_Reason"] = pd.Series("", index=df.index, dtype="string")

    # Reject invalid Customer_ID
    df.loc[df["Customer_ID"].isna(), "Reject_Reason"] = "Invalid Customer_ID"

    # Reject duplicate Customer_ID
    df.loc[df["Duplicate_Customer_ID"], "Reject_Reason"] = "Duplicate Customer_ID"

    df["Reject_Reason"] = df["Reject_Reason"].str.rstrip(", ")

    rejected_condition = df["Reject_Reason"] != ""
    rejected_df = df[rejected_condition].copy()
    cleaned_df = df[~rejected_condition].copy()

    

    os.makedirs("Cleaned_Data", exist_ok=True)
    os.makedirs("Rejected_Data", exist_ok=True)
    cleaned_df = cleaned_df.drop(columns=["Reject_Reason", "Duplicate_Customer_ID"])
    rejected_df = rejected_df.drop(columns=["Duplicate_Customer_ID"])
    cleaned_df["Created_at"] = pd.Timestamp.now()

    cleaned_df.to_csv("Cleaned_Data/valid_data/Customers.csv", index=False)
    rejected_df.to_csv("Cleaned_Data/Rejected_Data/Rejected_Customers.csv", index=False)

    logger.info(
        "Cleaning Summary: Total=%d, Clean=%d, Rejected=%d",
        len(df),
        len(cleaned_df),
        len(rejected_df),
    )
    if not rejected_df.empty:
        logger.info(
            "Sample Rejected Records:\n%s",
            rejected_df[["Customer_ID", "Reject_Reason"]].head(10).to_string(index=False),
        )
    logger.info("Customers.csv and Rejected_Customers.csv Saved Successfully.")
    return cleaned_df, rejected_df


def clean_customers(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Executes the entire customer data cleaning pipeline.

    Args:
        df (pd.DataFrame): Raw customer DataFrame.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: Tuple of (cleaned_df, rejected_df).
    """
    logger.info("=" * 60)
    logger.info("CUSTOMER CLEANING PIPELINE STARTED")
    logger.info("=" * 60)

    df = convert_customer_types(df)
    df = clean_customer_id(df)
    df = clean_missing_values(df)
    df = clean_duplicate_rows(df)
    df = clean_duplicate_customer_ids(df)
    df = clean_email(df)
    df = clean_phone(df)
    df = clean_registration_date(df)
    df = clean_gender(df)
    df = clean_city(df)
    df = clean_state(df)

    cleaned_df, rejected_df = split_clean_and_rejected(df)
    logger.info("=" * 60)
    logger.info("CUSTOMER CLEANING PIPELINE COMPLETED")
    logger.info("=" * 60)
    return cleaned_df, rejected_df