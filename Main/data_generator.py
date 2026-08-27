"""
data_generator.py

Orchestration module for triggering synthetic raw dataset generation.

Generates:
    - Raw_Data/Customers.csv (20,000 records)
    - Raw_Data/Products.csv (6,000 records)
    - Raw_Data/Orders.csv (140,000 records)
"""

import logging
import pandas as pd

from Scripts.generate_customers import generate_customers
from Scripts.generate_orders import generate_orders
from Scripts.generate_products import generate_products

logger = logging.getLogger(__name__)


def generate_csv_files() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Orchestrates the generation of all raw mock datasets.

    Returns:
        tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
            (customers_df, products_df, orders_df)
    """
    logger.info("Generating customer records...")
    customers_df = generate_customers()

    logger.info("Generating product records...")
    products_df = generate_products()

    logger.info("Generating order records...")
    orders_df = generate_orders()

    logger.info("All raw CSV files generated successfully.")
    return customers_df, products_df, orders_df


if __name__ == "__main__":
    generate_csv_files()
