"""
AppRun.py

Main entry point for orchestrating the Customer Sales ETL Pipeline.

Pipeline Workflow:
    1. Data Generation: Generates raw mock datasets (Customers, Products, Orders).
    2. Data Injection: Injects deliberate anomalies and data quality issues.
    3. Extraction: Loads raw datasets into pandas DataFrames.
    4. Transformation: Runs customer, product, and order cleaning pipelines.
    5. Loading: Truncates and loads cleaned & rejected records into MySQL tables.
    6. Reporting: Compiles and exports the final Data Quality Report.
"""

import logging
import os
import pandas as pd

from Main.sql_analysis import run_business_analysis
from Main.customer_cleaning import clean_customers
from Main.data_generator import generate_csv_files
from Main.data_injection import inject_raw_data
from Main.data_quality_report import generate_data_quality_report
from Main.database_loader import load_cleaned_data_to_db
from Main.order_cleaning import clean_orders
from Main.product_cleaning import clean_products
from Main.sales_transaction import create_sales_transaction_df


# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Central logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/etl_pipeline.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger("AppRun")


def main():
    """
    Executes the end-to-end Customer Sales ETL pipeline.

    Steps:
        1. Generates raw mock CSV datasets.
        2. Injects synthetic anomalies and corruptions.
        3. Reads the raw datasets into memory.
        4. Cleans customer records and separates rejected rows.
        5. Cleans product records and separates rejected rows.
        6. Cleans order records, validates foreign keys, and separates rejects.
        7. Truncates and loads all cleaned tables into MySQL.
        8. Generates the Data Quality Report CSV.
        9. Executes SQL Business Analysis.
    """
    logger.info("=" * 70)
    logger.info("CUSTOMER SALES ETL PIPELINE STARTED")
    logger.info("=" * 70)

    # -------------------------------------------------------------------------
    # Step 1: Generate Raw Datasets
    # -------------------------------------------------------------------------
    logger.info("Step 1: Generating Raw CSV Files...")
    generate_csv_files()

    # -------------------------------------------------------------------------
    # Step 2: Inject Data Quality Issues
    # -------------------------------------------------------------------------
    logger.info("Step 2: Injecting Data Quality Anomalies...")
    inject_raw_data()

    # -------------------------------------------------------------------------
    # Step 3: Load Raw CSV Datasets into Memory
    # -------------------------------------------------------------------------
    logger.info("Step 3: Loading Raw Datasets...")
    customers_raw = pd.read_csv("Raw_Data/Customers.csv", dtype={"Phone": str})
    products_raw = pd.read_csv("Raw_Data/Products.csv")
    orders_raw = pd.read_csv("Raw_Data/Orders.csv")

    # -------------------------------------------------------------------------
    # Step 4: Customer Cleaning Pipeline
    # -------------------------------------------------------------------------
    logger.info("Step 4: Running Customer Cleaning Pipeline...")
    clean_customers_df, rejected_customers_df = clean_customers(customers_raw)

    # -------------------------------------------------------------------------
    # Step 5: Product Cleaning Pipeline
    # -------------------------------------------------------------------------
    logger.info("Step 5: Running Product Cleaning Pipeline...")
    clean_products_df, rejected_products_df = clean_products(products_raw)

    # -------------------------------------------------------------------------
    # Step 6: Order Cleaning Pipeline
    # -------------------------------------------------------------------------
    logger.info("Step 6: Running Order Cleaning Pipeline...")
    clean_orders_df, rejected_orders_df = clean_orders(orders_raw)

    # -------------------------------------------------------------------------
    # Step 7: Create Sales Transaction Dataset
    # -------------------------------------------------------------------------
    logger.info("Step 7: Creating Sales Transaction Dataset...")

    sales_transaction_df = create_sales_transaction_df()
    # -------------------------------------------------------------------------
    # Step 8: Load to Database (Truncate & Insert)
    # -------------------------------------------------------------------------
    logger.info("Step 8: Loading Cleaned Datasets to Database...")
    load_cleaned_data_to_db(
        customers_df=clean_customers_df,
        products_df=clean_products_df,
        orders_df=clean_orders_df, 
        sales_transaction=sales_transaction_df   
    )
    
    # -------------------------------------------------------------------------
    # Step 9: Generate Data Quality Report
    # -------------------------------------------------------------------------
    logger.info("Step 9: Generating Data Quality Report...")
    generate_data_quality_report()

    # -------------------------------------------------------------------------
    # Step 10: SQL Business Analysis
    # -------------------------------------------------------------------------
    logger.info("Step 10: Running SQL Business Analysis...")
    run_business_analysis()

    logger.info("=" * 70)
    logger.info("CUSTOMER SALES ETL PIPELINE COMPLETED SUCCESSFULLY")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()