"""
generate_customers.py

Module for generating synthetic Indian customer profile data.

Outputs:
    Raw_Data/Customers.csv containing:
        - Customer_ID (e.g., CUST00001)
        - Customer_Name
        - Email
        - Phone (10-digit Indian mobile formats)
        - Gender (Male, Female)
        - City & State (Realistic Indian geographic pairs)
        - Registration_Date (Dates within the past 3 years)
"""

import os
import random
from faker import Faker
import pandas as pd
import logging
log = logging.getLogger(__name__)

def generate_customers(num_customers: int = 20000) -> pd.DataFrame:
    """
    Generates synthetic Indian customer records and writes them to Raw_Data/Customers.csv.

    Args:
        num_customers (int, optional): Number of customer records to generate.
            Defaults to 20000.

    Returns:
        pd.DataFrame: Generated customer records.
    """
    fake = Faker("en_IN")
    Faker.seed(42)
    random.seed(42)

    location_data = {
        "Tamil Nadu": [
            "Chennai", "Coimbatore", "Madurai", "Salem", "Trichy", "Erode", "Tirunelveli"],
        "Karnataka": [
            "Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi"],
        "Kerala": [
            "Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur" ],
        "Maharashtra": [
            "Mumbai", "Pune", "Nagpur", "Nashik", "Thane"],
        "Telangana": [
            "Hyderabad", "Warangal", "Karimnagar", "Nizamabad"],
        "Andhra Pradesh": [
            "Visakhapatnam", "Vijayawada", "Guntur", "Tirupati"],
        "Delhi": [
            "New Delhi"
        ],
        "Gujarat": [
            "Ahmedabad", "Surat", "Vadodara", "Rajkot"
        ],
        "West Bengal": [
            "Kolkata", "Howrah", "Durgapur", "Siliguri"
        ],
        "Uttar Pradesh": [
            "Lucknow", "Kanpur", "Noida", "Agra", "Varanasi"
        ],
        "Rajasthan": [
            "Jaipur", "Jodhpur", "Udaipur", "Kota"
        ],
        "Punjab": [
            "Ludhiana", "Amritsar", "Jalandhar"
        ],
        "Haryana": [
            "Gurugram", "Faridabad", "Panipat"
        ],
        "Madhya Pradesh": [
            "Indore", "Bhopal", "Jabalpur"
        ],
    }

    genders = ["Male", "Female","others"]
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "Raw_Data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "Customers.csv")

    customers = []
    for i in range(1, num_customers + 1):
        state = random.choice(list(location_data.keys()))
        city = random.choice(location_data[state])

        # 10-digit Indian mobile format beginning with 6-9
        phone = random.choice(["6", "7", "8", "9"]) + "".join(
            random.choices("0123456789", k=9)
        )

        customer = {
            "Customer_ID": f"CUST{i:05d}",
            "Customer_Name": fake.name(),
            "Email": fake.email(),
            "Phone": phone,
            "Gender": random.choice(genders),
            "City": city,
            "State": state,
            "Registration_Date": fake.date_between(
                start_date="-3y",
                end_date="today"
            ),
        }
        customers.append(customer)

    customers_df = pd.DataFrame(customers)
    customers_df["Registration_Date"] = pd.to_datetime(
        customers_df["Registration_Date"]
    ).dt.strftime("%Y-%m-%d")

    customers_df.to_csv(output_file, index=False)

    log.info("=" * 50)
    log.info("Customers Dataset Generated Successfully")
    log.info(f"Total Customers : {len(customers_df):,}")
    log.info(f"Output File     : {output_file}")
    log.info("=" * 50)

    return customers_df


if __name__ == "__main__":
    generate_customers()