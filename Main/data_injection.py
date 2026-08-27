"""
data_injection.py

Orchestration module for injecting intentional data quality corruptions and
anomalies into raw CSV datasets (Customers, Products, Orders).
"""

import logging
import pandas as pd

from Scripts.inject_customer import inject_customers
from Scripts.inject_order import inject_orders
from Scripts.inject_product import inject_products

logger = logging.getLogger(__name__)


def inject_raw_data(error_count: int = 20) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Injects synthetic data quality issues into raw CSV datasets.

    Args:
        error_count (int, optional): Number of corrupted rows per error category.
            Defaults to 20.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
            (customers_df, products_df, orders_df)
    """
    logger.info("Injecting data quality issues into Customers.csv...")
    customers_df = inject_customers(error_count=error_count)

    logger.info("Injecting data quality issues into Products.csv...")
    products_df = inject_products(error_count=error_count)

    logger.info("Injecting data quality issues into Orders.csv...")
    orders_df = inject_orders(error_count=error_count)

    logger.info("All data quality issues injected successfully.")
    return customers_df, products_df, orders_df


if __name__ == "__main__":
    inject_raw_data()
