"""
File : inject_order.py

Description:
Injects data quality issues into Raw_Data/Orders.csv
"""

import os
import random
import pandas as pd
import logging

log = logging.getLogger(__name__)

def inject_orders(error_count=20):
    random.seed(42)

    # =====================================================
    # File Path
    # =====================================================
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    order_file = os.path.join(
        base_dir,
        "Raw_Data",
        "Orders.csv"
    )

    # =====================================================
    # Read CSV
    # =====================================================
    df = pd.read_csv(order_file, dtype=str)
    df["Quantity"] = pd.to_numeric(df["Quantity"])

    # =====================================================
    # Helper
    # =====================================================
    used_indexes = set()

    def get_indexes(count):
        available = list(set(df.index) - used_indexes)
        indexes = random.sample(available, min(count, len(available)))
        used_indexes.update(indexes)
        return indexes

    # =====================================================
    # Injection Functions
    # =====================================================
    def missing_payment_method():
        idx = get_indexes(error_count)
        df.loc[idx, "Payment_Method"] = None
        return len(idx)

    def missing_order_status():
        idx = get_indexes(error_count)
        df.loc[idx, "Order_Status"] = None
        return len(idx)

    def negative_quantity():
        idx = get_indexes(error_count)
        for i in idx:
            df.at[i, "Quantity"] = -random.randint(1, 10)
        return len(idx)

    def zero_quantity():
        idx = get_indexes(error_count)
        df.loc[idx, "Quantity"] = 0
        return len(idx)

    def duplicate_order_id():
        idx = get_indexes(error_count)
        for i in idx:
            another = random.randint(0, len(df) - 1)
            df.at[i, "Order_ID"] = df.at[another, "Order_ID"]
        return len(idx)

    def duplicate_record():
        idx = get_indexes(error_count)
        for i in idx:
            another = random.randint(0, len(df) - 1)
            df.loc[i] = df.loc[another]
        return len(idx)

    def invalid_customer_id():
        idx = get_indexes(error_count)
        for i in idx:
            df.at[i, "Customer_ID"] = f"CUST{random.randint(90000, 99999)}"
        return len(idx)

    def invalid_product_id():
        idx = get_indexes(error_count)
        for i in idx:
            df.at[i, "Product_ID"] = f"PROD{random.randint(90000, 99999)}"
        return len(idx)

    def invalid_order_date():
        idx = get_indexes(error_count)
        invalid_dates = [
            "2025-15-12",
            "32-01-2024",
            "abcd",
            "2024/99/10",
            "31-13-2025"
        ]
        for i in idx:
            df.at[i, "Order_Date"] = random.choice(invalid_dates)
        return len(idx)

    def future_order_date():
        idx = get_indexes(error_count)
        future_dates = [
            "2030-01-15",
            "2032-05-10",
            "2040-11-25",
            "2035-07-01"
        ]
        for i in idx:
            df.at[i, "Order_Date"] = random.choice(future_dates)
        return len(idx)

    # =====================================================
    # Execute
    # =====================================================
    summary = {
        "Missing Payment Method": missing_payment_method(),
        "Missing Order Status": missing_order_status(),
        "Negative Quantity": negative_quantity(),
        "Zero Quantity": zero_quantity(),
        "Duplicate Order_ID": duplicate_order_id(),
        "Duplicate Record": duplicate_record(),
        "Invalid Customer_ID": invalid_customer_id(),
        "Invalid Product_ID": invalid_product_id(),
        "Invalid Order Date": invalid_order_date(),
        "Future Order Date": future_order_date(),
    }

    # =====================================================
    # Save
    # =====================================================
    df.to_csv(order_file, index=False)

    # =====================================================
    # Summary
    # =====================================================
    ("\n" + "=" * 60)
    log.info("Order Injection Completed")
    log.info("=" * 60)
    for k, v in summary.items():
        log.info(f"{k:<30}: {v}")
    log.info("=" * 60)
    log.info(f"Total Modified Rows : {len(used_indexes)}")
    log.info(f"Output File         : {order_file}")
    log.info("=" * 60)

    return df

if __name__ == "__main__":
    inject_orders()