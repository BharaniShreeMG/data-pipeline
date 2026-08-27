"""
database_loader.py



Capabilities:
    - Automatically provisions MySQL database if it does not exist.
    - Creates target DDL schemas for Cleaned tables (customers, products, orders).
    - Truncates existing tables prior to load to guarantee idempotence.
    - Performs chunked batch inserts via cursor.executemany().
    - Converts NaN/NaT values to SQL NULLs.
"""

import logging
import os
from typing import Any, Optional

import mysql.connector
from mysql.connector.cursor import MySQLCursor
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Default MySQL connection configuration (can be overridden via environment variables)
DEFAULT_CONFIG: dict[str, Any] = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "customer_sales_db"),
}

TABLE_SCHEMAS: dict[str, str] = {
    # Cleaned Tables
    "customers": """
        CREATE TABLE IF NOT EXISTS customers (
            Customer_ID VARCHAR(20) PRIMARY KEY,
            Customer_Name VARCHAR(100),
            Email VARCHAR(100),
            Phone VARCHAR(20),
            Gender VARCHAR(20),
            City VARCHAR(50),
            State VARCHAR(50),
            Registration_Date DATE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "products": """
        CREATE TABLE IF NOT EXISTS products (
            Product_ID VARCHAR(20) PRIMARY KEY,
            Product_Name VARCHAR(150),
            Category VARCHAR(50),
            Sub_Category VARCHAR(50),
            Price DECIMAL(10, 2),
            Supplier VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "orders": """
        CREATE TABLE IF NOT EXISTS orders (
            Order_ID VARCHAR(20) PRIMARY KEY,
            Customer_ID VARCHAR(20),
            Product_ID VARCHAR(20),
            Order_Date DATE,
            Quantity INT,
            Payment_Method VARCHAR(50),
            Order_Status VARCHAR(50),
            FOREIGN KEY (Customer_ID)REFERENCES customers(Customer_ID),
            FOREIGN KEY (Product_ID)REFERENCES products(Product_ID)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """,
    "sales_transaction": """
CREATE TABLE IF NOT EXISTS sales_transaction (
    Order_ID VARCHAR(20) PRIMARY KEY,
    Order_Date DATE,

    Customer_ID VARCHAR(20),
    Customer_Name VARCHAR(100),
    City VARCHAR(50),
    State VARCHAR(50),

    Product_ID VARCHAR(20),
    Product_Name VARCHAR(150),
    Category VARCHAR(50),
    Sub_Category VARCHAR(50),

    Quantity INT,
    Price DECIMAL(10,2),
    Total_Amount DECIMAL(12,2),

    Payment_Method VARCHAR(50),
    Order_Status VARCHAR(50),

    Order_Year INT,
    Order_Month VARCHAR(20),
    YearMonth VARCHAR(20)
) ENGINE=InnoDB;
""",
}


def get_connection(
    config: Optional[dict[str, Any]] = None,
    create_db: bool = True
) -> mysql.connector.MySQLConnection:
    """
    Establishes and returns a MySQL database connection.

    Args:
        config (dict[str, Any], optional): MySQL connection parameters.
            Defaults to DEFAULT_CONFIG.
        create_db (bool, optional): Whether to ensure the database exists.
            Defaults to True.

    Returns:
        mysql.connector.MySQLConnection: Active MySQL connection.
    """
    cfg = dict(config or DEFAULT_CONFIG)

    if create_db:
        server_cfg = {k: v for k, v in cfg.items() if k != "database"}
        conn = mysql.connector.connect(**server_cfg)
        cursor = conn.cursor()
        db_name = cfg["database"]
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
            f"DEFAULT CHARACTER SET utf8mb4;"
        )
        cursor.close()
        conn.close()

    return mysql.connector.connect(**cfg)


def prepare_data_for_insert(df: pd.DataFrame) -> list[tuple[Any, ...]]:
    """
    Replaces pandas NA/NaN/NaT values with Python None for SQL NULL mapping.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        list[tuple[Any, ...]]: List of row tuples ready for parameterized insert.
    """
    cleaned_df = df.copy()
    cleaned_df = cleaned_df.replace({np.nan: None, pd.NA: None})
    return [
        tuple(None if pd.isna(val) else val for val in row)
        for row in cleaned_df.itertuples(index=False, name=None)
    ]


def load_table(
    cursor: MySQLCursor,
    table_name: str,
    df: Optional[pd.DataFrame],
    batch_size: int = 5000,
) -> None:
    """
    Provisions schema DDL, truncates old data, and bulk-inserts rows in batches.

    Args:
        cursor (MySQLCursor): Database cursor.
        table_name (str): Target table name.
        df (pd.DataFrame, optional): Data to insert into table.
        batch_size (int, optional): Batch size for executemany. Defaults to 5000.
    """
    logger.info("Setting up table '%s'...", table_name)

    # 1. Create table if not exists
    cursor.execute(TABLE_SCHEMAS[table_name])

    # 2. Truncate existing data
    logger.info("Truncating existing data in table '%s'...", table_name)
    cursor.execute(f"TRUNCATE TABLE `{table_name}`;")

    # 3. Batch insert fresh records
    if df is not None and not df.empty:
        columns = list(df.columns)
        col_names = ", ".join([f"`{c}`" for c in columns])
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"INSERT INTO `{table_name}` ({col_names}) VALUES ({placeholders});"

        rows = prepare_data_for_insert(df)
        total_rows = len(rows)

        logger.info("Inserting %d rows into '%s'...", total_rows, table_name)
        for start in range(0, total_rows, batch_size):
            batch = rows[start:start + batch_size]
            cursor.executemany(insert_sql, batch)

        logger.info("Successfully loaded %d records into '%s'.", total_rows, table_name)
    else:
        logger.info("No records to insert into '%s'.", table_name)


def load_cleaned_data_to_db(
    customers_df: Optional[pd.DataFrame] = None,
    products_df: Optional[pd.DataFrame] = None,
    orders_df: Optional[pd.DataFrame] = None,
    sales_transaction: Optional[pd.DataFrame] = None,
    config: Optional[dict[str, Any]] = None,
) -> None:
    """
    Orchestrates truncation and batch loading of clean datasets into MySQL.

    Args:
        customers_df (pd.DataFrame, optional): Clean customer records.
        products_df (pd.DataFrame, optional): Clean product records.
        orders_df (pd.DataFrame, optional): Clean order records.
        config (dict[str, Any], optional): MySQL connection config override.
    """
    logger.info("=" * 60)
    logger.info("MYSQL DATABASE LOADING PIPELINE STARTED")
    logger.info("=" * 60)

    # Fallback to loading from CSV files on disk if DataFrames are omitted
    if customers_df is None:
        customers_df = pd.read_csv("Cleaned_Data/valid_data/Customers.csv")

    if products_df is None:
        products_df = pd.read_csv("Cleaned_Data/valid_data/Products.csv")
    

    if orders_df is None:
        orders_df = pd.read_csv("Cleaned_Data/valid_data/Orders.csv")
    
    if sales_transaction is None:
        sales_transaction = pd.read_csv(
            "Cleaned_Data/valid_data/Sales_Transaction.csv"
        )
    
    conn = get_connection(config=config)
    cursor = conn.cursor()

    try:
        # Load Cleaned Tables
        load_table(cursor, "customers", customers_df)
        load_table(cursor, "products", products_df)
        load_table(cursor, "orders", orders_df)
        load_table(cursor,"sales_transaction",sales_transaction)


        conn.commit()
        logger.info("=" * 60)
        logger.info("ALL CLEANED & REJECTED DATA LOADED TO MYSQL DATABASE SUCCESSFULLY")
        logger.info("=" * 60)

    except Exception as e:
        conn.rollback()
        logger.error("Database loading failed: %s", e)
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    load_cleaned_data_to_db()
