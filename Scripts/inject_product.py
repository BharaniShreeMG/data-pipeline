"""
File : inject_product.py

Description:
Injects data quality issues into Raw_Data/Products.csv
"""

import os
import random
import pandas as pd
import logging
log = logging.getLogger(__name__)


def inject_products(error_count=20):
    random.seed(42)

    # ===========================================
    # File Path
    # ===========================================
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    product_file = os.path.join(
        base_dir,
        "Raw_Data",
        "Products.csv"
    )

    # ===========================================
    # Read CSV
    # ===========================================
    df = pd.read_csv(product_file, dtype=str)

    # Convert Price to numeric for modification
    df["Price"] = pd.to_numeric(df["Price"])

    # ===========================================
    # Helper
    # ===========================================
    used_indexes = set()

    def get_indexes(count):
        available = list(set(df.index) - used_indexes)
        indexes = random.sample(available, min(count, len(available)))
        used_indexes.update(indexes)
        return indexes

    # ===========================================
    # Injection Functions
    # ===========================================
    def missing_product_name():
        idx = get_indexes(error_count)
        df.loc[idx, "Product_Name"] = None
        return len(idx)

    def missing_supplier():
        idx = get_indexes(error_count)
        df.loc[idx, "Supplier"] = None
        return len(idx)

    def negative_price():
        idx = get_indexes(error_count)
        for i in idx:
            df.at[i, "Price"] = -random.randint(100, 5000)
        return len(idx)

    def zero_price():
        idx = get_indexes(error_count)
        df.loc[idx, "Price"] = 0
        return len(idx)

    def duplicate_product_id():
        idx = get_indexes(error_count)
        for i in idx:
            another = random.randint(0, len(df) - 1)
            df.at[i, "Product_ID"] = df.at[another, "Product_ID"]
        return len(idx)

    def duplicate_record():
        idx = get_indexes(error_count)
        for i in idx:
            another = random.randint(0, len(df) - 1)
            df.loc[i] = df.loc[another]
        return len(idx)

    def missing_category():
        idx = get_indexes(error_count)
        df.loc[idx, "Category"] = None
        return len(idx)

    def missing_sub_category():
        idx = get_indexes(error_count)
        df.loc[idx, "Sub_Category"] = None
        return len(idx)

    def inconsistent_category():
        idx = get_indexes(error_count)
        mapping = {
            "Electronics": [
                "electronics",
                " ELECTRONICS ",
                "ELECTRONICS"
            ],
            "Fashion": [
                "fashion",
                " FASHION ",
                "FASHION"
            ],
            "Books": [
                "books",
                " BOOKS ",
                "BOOKS"
            ],
            "Beauty": [
                "beauty",
                " BEAUTY ",
                "BEAUTY"
            ],
            "Sports": [
                "sports",
                " SPORTS ",
                "SPORTS"
            ],
            "Grocery": [
                "grocery",
                " GROCERY ",
                "GROCERY"
            ],
            "Home & Kitchen": [
                "home & kitchen",
                " HOME & KITCHEN ",
                "HOME & KITCHEN"
            ]
        }

        for i in idx:
            cat = df.at[i, "Category"]
            if cat in mapping:
                df.at[i, "Category"] = random.choice(mapping[cat])

        return len(idx)

    # ===========================================
    # Execute
    # ===========================================
    summary = {
        "Missing Product Name": missing_product_name(),
        "Missing Supplier": missing_supplier(),
        "Negative Price": negative_price(),
        "Zero Price": zero_price(),
        "Duplicate Product_ID": duplicate_product_id(),
        "Duplicate Record": duplicate_record(),
        "Missing Category": missing_category(),
        "Missing Sub Category": missing_sub_category(),
        "Inconsistent Category": inconsistent_category(),
    }

    # ===========================================
    # Save
    # ===========================================
    df.to_csv(product_file, index=False)

    # ===========================================
    # Summary
    # ===========================================
    log.info("\n" + "=" * 60)
    log.info("Product Injection Completed")
    log.info("=" * 60)
    for k, v in summary.items():
        log.info(f"{k:<30}: {v}")
    log.info("=" * 60)
    log.info(f"Total Modified Rows : {len(used_indexes)}")
    log.info(f"Output File         : {product_file}")
    log.info("=" * 60)

    return df