"""
inject_customer.py

Module for injecting controlled data quality corruptions into Raw_Data/Customers.csv.

Injected Quality Issues:
    - Missing & malformed phone numbers (9 or 12 digits).
    - Missing & malformed email addresses (invalid RFC formats).
    - Duplicate Customer_IDs and fully duplicate records.
    - Invalid & future registration dates.
    - Missing & inconsistent city / state casings.
"""

import os
import random
import pandas as pd
import logging
log = logging.getLogger(__name__)


def inject_customers(error_count: int = 20) -> pd.DataFrame:
    """
    Injects synthetic data quality issues into Raw_Data/Customers.csv.

    Args:
        error_count (int, optional): Number of corrupted rows per error category.
            Defaults to 20.

    Returns:
        pd.DataFrame: Mutated customer DataFrame with injected errors.
    """
    random.seed(42)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    customer_file = os.path.join(base_dir, "Raw_Data", "Customers.csv")

    df = pd.read_csv(customer_file, dtype=str)
    used_indexes: set[int] = set()

    def get_indexes(count: int) -> list[int]:
        """Returns unused row indices to avoid corrupting the same row twice."""
        available = list(set(df.index) - used_indexes)
        indexes = random.sample(available, min(count, len(available)))
        used_indexes.update(indexes)
        return indexes

    def inject_missing_phone() -> int:
        indexes = get_indexes(error_count)
        df.loc[indexes, "Phone"] = None
        return len(indexes)

    def inject_invalid_phone() -> int:
        indexes = get_indexes(error_count)
        for idx in indexes:
            if random.random() < 0.5:
                df.at[idx, "Phone"] = "987654321"       # 9 digits
            else:
                df.at[idx, "Phone"] = "987654321012"    # 12 digits
        return len(indexes)

    def inject_missing_email() -> int:
        indexes = get_indexes(error_count)
        df.loc[indexes, "Email"] = None
        return len(indexes)

    def inject_invalid_email() -> int:
        indexes = get_indexes(error_count)
        invalid = [
            "USER @gmail.com",
            "TEST @gmail.COM",
            "abcgmail.com",
            "name@@gmail.com",
            "user name@gmail.com",
        ]
        for idx in indexes:
            df.at[idx, "Email"] = random.choice(invalid)
        return len(indexes)

    def inject_duplicate_customer_id() -> int:
        indexes = get_indexes(error_count)
        for idx in indexes:
            random_row = random.randint(0, len(df) - 1)
            df.at[idx, "Customer_ID"] = df.at[random_row, "Customer_ID"]
        return len(indexes)

    def inject_duplicate_records() -> int:
        indexes = get_indexes(error_count)
        for idx in indexes:
            random_row = random.randint(0, len(df) - 1)
            df.loc[idx] = df.loc[random_row]
        return len(indexes)

    def inject_invalid_registration_date() -> int:
        indexes = get_indexes(error_count)
        invalid_dates = [
            "2035-01-01",
            "32-12-2025",
            "2025-15-20",
            "abcd",
            "2024/99/15",
        ]
        for idx in indexes:
            df.at[idx, "Registration_Date"] = random.choice(invalid_dates)
        return len(indexes)

    def inject_missing_city() -> int:
        indexes = get_indexes(error_count)
        df.loc[indexes, "City"] = None
        return len(indexes)

    def inject_missing_state() -> int:
        indexes = get_indexes(error_count)
        df.loc[indexes, "State"] = None
        return len(indexes)

    def inject_inconsistent_city() -> int:
        indexes = get_indexes(error_count)
        city_map = {
            "Chennai": ["chennai", "CHENNAI", " Chennai "],
            "Mumbai": ["mumbai", "MUMBAI", " Mumbai "],
            "Bengaluru": ["bengaluru", "BENGALURU", " Bengaluru "],
            "Hyderabad": ["hyderabad", "HYDERABAD"],
            "Kolkata": ["kolkata", "KOLKATA"],
            "Pune": ["pune", "PUNE"],
        }
        for idx in indexes:
            city = df.at[idx, "City"]
            if city in city_map:
                df.at[idx, "City"] = random.choice(city_map[city])
        return len(indexes)

    summary = {
        "Missing Phone": inject_missing_phone(),
        "Invalid Phone": inject_invalid_phone(),
        "Missing Email": inject_missing_email(),
        "Invalid Email": inject_invalid_email(),
        "Duplicate Customer_ID": inject_duplicate_customer_id(),
        "Duplicate Record": inject_duplicate_records(),
        "Invalid Registration Date": inject_invalid_registration_date(),
        "Missing City": inject_missing_city(),
        "Missing State": inject_missing_state(),
        "Inconsistent City": inject_inconsistent_city(),
    }

    df.to_csv(customer_file, index=False)

    log.info("\n" + "=" * 60)
    log.info("Customer Injection Completed")
    log.info("=" * 60)
    for key, value in summary.items():
        log.info(f"{key:<30}: {value}")
    log.info("=" * 60)
    log.info(f"Total Modified Rows : {len(used_indexes)}")
    log.info(f"Output File         : {customer_file}")
    log.info("=" * 60)

    return df


if __name__ == "__main__":
    inject_customers()