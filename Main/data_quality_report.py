"""
data_quality_report.py

Module for aggregating quality metrics and generating validation summaries.

Calculates:
    - Total record counts across all datasets (Customers, Products, Orders).
    - Clean vs. Rejected record distribution.
    - Data validation status ('Passed' or 'Completed with Rejections').
    - Exports the final audit summary to Reports/Data_Quality_Report.csv.
"""

import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)


def generate_data_quality_report() -> pd.DataFrame:
    """
    Reads cleaned and rejected CSV datasets, computes summary statistics,
    and exports the audit report to Reports/Data_Quality_Report.csv.

    Returns:
        pd.DataFrame: Data Quality summary report DataFrame.
    """
    logger.info("Generating Data Quality Report...")

    # Load cleaned and rejected datasets
    customers = pd.read_csv("Cleaned_Data/valid_data/Customers.csv")
    rejected_customers = pd.read_csv("Cleaned_Data/Rejected_Data/Rejected_Customers.csv")

    products = pd.read_csv("Cleaned_Data/valid_data/Products.csv")
    rejected_products = pd.read_csv("Cleaned_Data/Rejected_Data/Rejected_Products.csv")

    orders = pd.read_csv("Cleaned_Data/valid_data/Orders.csv")
    rejected_orders = pd.read_csv("Cleaned_Data/Rejected_Data/Rejected_Orders.csv")

    report = pd.DataFrame({
        "Dataset": ["Customers", "Products", "Orders"],
        "Total_Records": [
            len(customers) + len(rejected_customers),
            len(products) + len(rejected_products),
            len(orders) + len(rejected_orders),
        ],
        "Clean_Records": [
            len(customers),
            len(products),
            len(orders),
        ],
        "Rejected_Records": [
            len(rejected_customers),
            len(rejected_products),
            len(rejected_orders),
        ],
    })

    report["Validation_Status"] = report["Rejected_Records"].apply(
        lambda x: "Passed" if x == 0 else "Completed with Rejections"
    )

    os.makedirs("Reports", exist_ok=True)
    report_path = "Reports/Data_Quality_Report.csv"
    report.to_csv(report_path, index=False)

    logger.info("\n%s", report.to_string(index=False))
    logger.info(
        "Data_Quality_Report.csv Generated Successfully at '%s'.",
        report_path
    )

    return report


if __name__ == "__main__":
    generate_data_quality_report()