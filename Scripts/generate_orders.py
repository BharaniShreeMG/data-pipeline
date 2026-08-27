"""
generate_orders.py

Module for generating synthetic sales transaction orders.

Outputs:
    Raw_Data/Orders.csv containing:
        - Order_ID
        - Customer_ID
        - Product_ID
        - Order_Date
        - Quantity
        - Payment_Method
        - Order_Status
"""

import os
import random
from datetime import datetime, timedelta
import logging

log = logging.getLogger(__name__)
import pandas as pd


def generate_orders(
    num_orders: int = 140000,
    num_customers: int = 20000,
    num_products: int = 6000,
) -> pd.DataFrame:
    """
    Generates synthetic customer orders.

    Returns
    -------
    pd.DataFrame
    """

    random.seed(42)

    payment_methods = [
        "UPI",
        "Credit Card",
        "Debit Card",
        "Net Banking",
        "Cash on Delivery",
        "Wallet",
    ]

    order_status = [
        "Completed",
        "Completed",
        "Completed",
        "Completed",
        "Pending",
        "Cancelled",
        "Returned",
    ]

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    raw_data = os.path.join(base_dir, "Raw_Data")
    os.makedirs(raw_data, exist_ok=True)

    output_file = os.path.join(raw_data, "Orders.csv")

    today = datetime.today()
    start_date = today - timedelta(days=540)

    # -----------------------------------------------------
    # Customer Distribution
    # -----------------------------------------------------

    customer_ids = [
        f"CUST{i:05d}"
        for i in range(1, num_customers + 1)
    ]

    customer_weights = []

    for i in range(num_customers):

        if i < int(num_customers * 0.10):
            # Top 10%
            customer_weights.append(random.randint(12, 20))

        elif i < int(num_customers * 0.30):
            # Next 20%
            customer_weights.append(random.randint(5, 10))

        else:
            # Remaining customers
            customer_weights.append(random.randint(1, 3))
    # Build weighted customer pool
    customer_pool = []

    for customer, weight in zip(customer_ids, customer_weights):
        customer_pool.extend([customer] * weight)

    # -----------------------------------------------------
    # Product Distribution
    # -----------------------------------------------------

    product_ids = [
        f"PROD{i:05d}"
        for i in range(1, num_products + 1)
    ]

    product_weights = []

    for i in range(num_products):

        if i < int(num_products * 0.10):
            product_weights.append(random.randint(10, 15))

        elif i < int(num_products * 0.30):
            product_weights.append(random.randint(4, 8))

        else:
            product_weights.append(random.randint(1, 3))
    # Build weighted product pool
    product_pool = []

    for product, weight in zip(product_ids, product_weights):
        product_pool.extend([product] * weight)

    # -----------------------------------------------------
    # Generate Orders
    # -----------------------------------------------------

    orders = []

    for i in range(1, num_orders + 1):

        order_date = (
            start_date +
            timedelta(days=random.randint(0, 540))
        ).strftime("%Y-%m-%d")

        customer_id = random.choice(customer_pool)

        product_id = random.choice(product_pool)

        quantity = random.choices(
            population=[1,2,3,4,5,6,7,8],
            weights=[40,25,15,8,5,3,2,2],
            k=1
        )[0]

        orders.append({

            "Order_ID": f"ORD{i:06d}",

            "Customer_ID": customer_id,

            "Product_ID": product_id,

            "Order_Date": order_date,

            "Quantity": quantity,

            "Payment_Method": random.choice(payment_methods),

            "Order_Status": random.choice(order_status),

        })

    orders_df = pd.DataFrame(orders)

    orders_df.to_csv(output_file, index=False)

    log.info("=" * 60)
    log.info("Orders Dataset Generated Successfully")
    log.info(f"Total Orders : {len(orders_df):,}")
    log.info(f"Output File  : {output_file}")
    log.info("=" * 60)

    return orders_df


if __name__ == "__main__":
    generate_orders()