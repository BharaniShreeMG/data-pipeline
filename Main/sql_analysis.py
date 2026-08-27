"""
sql_analysis.py

Description:
    Executes all SQL queries from business_analysis.sql
    and prints the results to the console.
"""

import logging
import os

import mysql.connector
import sqlparse

logger = logging.getLogger(__name__)


def run_business_analysis():
    """
    Executes all SQL queries from SQL/business_analysis.sql
    and prints the results.
    """

    logger.info("=" * 60)
    logger.info("SQL BUSINESS ANALYSIS STARTED")
    logger.info("=" * 60)

    conn = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        port=int(os.environ.get("MYSQL_PORT", 3306)),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "customer_sales_db"),
    )

    cursor = conn.cursor()

    sql_file = "SQL/business_analysis.sql"

    with open(sql_file, "r", encoding="utf-8") as file:
        sql_script = file.read()

    # Remove SQL comments
    sql_script = sqlparse.format(
        sql_script,
        strip_comments=True
    )

    # Correctly split SQL statements
    queries = [
        query.strip()
        for query in sqlparse.split(sql_script)
        if query.strip()
    ]

    for index, query in enumerate(queries, start=1):

        print("\n" + "=" * 80)
        print(f"QUERY {index}")
        print("=" * 80)

        try:
            cursor.execute(query)

            if cursor.with_rows:

                columns = [col[0] for col in cursor.description]

                print(" | ".join(columns))
                print("-" * 80)

                rows = cursor.fetchall()

                # Print first 10 rows only
                for row in rows[:10]:
                    print(" | ".join(str(value) for value in row))

                if len(rows) > 10:
                    print(f"\nShowing first 10 of {len(rows)} rows...")

                print(f"\nTotal Rows : {len(rows)}")

            else:
                conn.commit()
                print("Query executed successfully.")

        except mysql.connector.Error as err:
            print(f"\nError in Query {index}")
            print(err)
            print("\nQuery:")
            print(query)

    cursor.close()
    conn.close()

    logger.info("=" * 60)
    logger.info("SQL BUSINESS ANALYSIS COMPLETED")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_business_analysis()