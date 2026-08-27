"""
generate_products.py

Module for generating synthetic product catalog records with realistic
Indian brands, retail suppliers, categories, and price bands.

Outputs:
    Raw_Data/Products.csv containing:
        - Product_ID (e.g., PROD00001)
        - Product_Name (Brand + Sub_Category)
        - Category & Sub_Category
        - Price (Category-specific numeric price ranges)
        - Supplier
"""

import os
import random
import pandas as pd
import logging

log = logging.getLogger(__name__)

def generate_products(num_products: int = 6000) -> pd.DataFrame:
    """
    Generates synthetic product records and writes them to Raw_Data/Products.csv.

    Args:
        num_products (int, optional): Number of product records to generate.
            Defaults to 6000.

    Returns:
        pd.DataFrame: Generated product records.
    """
    random.seed(42)

    category_data = {
        "Electronics": [
            "Mobile", "Laptop", "Smart Watch", "Headphones", "Television"
        ],
        "Fashion": [
            "Men T-Shirt", "Women Dress", "Jeans", "Shoes", "Handbag"
        ],
        "Home & Kitchen": [
            "Mixer Grinder", "Pressure Cooker", "Dining Table", "Sofa", "LED Lamp"
        ],
        "Beauty": [
            "Face Wash", "Shampoo", "Perfume", "Lipstick"
        ],
        "Books": [
            "Academic Book", "Novel", "Biography", "Children Book"
        ],
        "Sports": [
            "Cricket Bat", "Football", "Dumbbell", "Badminton Racket"
        ],
        "Grocery": [
            "Rice", "Cooking Oil", "Tea Powder", "Biscuits", "Spices"
        ],
    }

    brands = [
        "Tata", "Reliance", "Prestige", "Samsung", "LG", "Sony", "Bajaj",
        "Puma", "Nike", "Adidas", "Boat", "Amul", "Aashirvaad", "Godrej",
        "Dell", "HP", "Lenovo", "Apple", "Mi", "OnePlus",
    ]

    suppliers = [
        "Reliance Retail", "Flipkart Seller", "Amazon Seller", "DMart",
        "BigBasket", "Croma", "Vijay Sales", "Tata Consumer", "ITC Limited",
        "Godrej Consumer",
    ]

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data = os.path.join(base_dir, "Raw_Data")
    os.makedirs(raw_data, exist_ok=True)
    output_file = os.path.join(raw_data, "Products.csv")

    products = []
    for i in range(1, num_products + 1):
        category = random.choice(list(category_data.keys()))
        sub_category = random.choice(category_data[category])
        product_name = f"{random.choice(brands)} {sub_category}"

        # Category-wise Realistic Pricing
        if category == "Electronics":
            price = random.randint(5000, 150000)
        elif category == "Fashion":
            price = random.randint(300, 8000)
        elif category == "Home & Kitchen":
            price = random.randint(500, 50000)
        elif category == "Beauty":
            price = random.randint(100, 5000)
        elif category == "Books":
            price = random.randint(150, 2500)
        elif category == "Sports":
            price = random.randint(500, 30000)
        else:  # Grocery
            price = random.randint(50, 3000)

        products.append({
            "Product_ID": f"PROD{i:05d}",
            "Product_Name": product_name,
            "Category": category,
            "Sub_Category": sub_category,
            "Price": price,
            "Supplier": random.choice(suppliers),
        })

    products_df = pd.DataFrame(products)
    products_df.to_csv(output_file, index=False)

    log.info("=" * 50)
    log.info("Products Dataset Generated Successfully")
    log.info(f"Total Products : {len(products_df):,}")
    log.info(f"Output File    : {output_file}")
    log.info("=" * 50)

    return products_df


if __name__ == "__main__":
    generate_products()