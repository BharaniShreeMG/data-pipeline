-- ==========================================================
-- CUSTOMER SALES ETL PROJECT
-- BUSINESS ANALYSIS QUERIES
-- ==========================================================

-- ==========================================================
-- CUSTOMER ANALYSIS
-- ==========================================================

-- 1. Total Registered Customers

SELECT
COUNT(*) AS Total_Registered_Customers
FROM customers;


-- ==========================================================

-- 2. Top 10 Customers by Total Spending

SELECT
    c.Customer_ID,
    c.Customer_Name,
    ROUND(SUM(p.Price * o.Quantity),2) AS Total_Spending
FROM customers c
JOIN orders o
ON c.Customer_ID = o.Customer_ID
JOIN products p
ON o.Product_ID = p.Product_ID
GROUP BY
    c.Customer_ID,
    c.Customer_Name
ORDER BY Total_Spending DESC
LIMIT 10;


-- ==========================================================

-- 3. Customers Who Never Placed an Order

SELECT
    c.Customer_ID,
    c.Customer_Name
FROM customers c
LEFT JOIN orders o
ON c.Customer_ID = o.Customer_ID
WHERE o.Order_ID IS NULL;


-- ==========================================================

-- 4. Customers With More Than 5 Orders

SELECT
    c.Customer_ID,
    c.Customer_Name,
    COUNT(o.Order_ID) AS Total_Orders
FROM customers c
JOIN orders o
ON c.Customer_ID = o.Customer_ID
GROUP BY
    c.Customer_ID,
    c.Customer_Name
HAVING COUNT(o.Order_ID) > 5
ORDER BY Total_Orders DESC;


-- ==========================================================

-- 5. City Having Highest Number of Customers

SELECT
    City,
    COUNT(*) AS Customer_Count
FROM customers
GROUP BY City
ORDER BY Customer_Count DESC
LIMIT 1;


-- ==========================================================
-- PRODUCT & SALES ANALYSIS
-- ==========================================================

-- 6. Top 10 Products By Quantity Sold

SELECT
    p.Product_ID,
    p.Product_Name,
    SUM(o.Quantity) AS Quantity_Sold
FROM products p
JOIN orders o
ON p.Product_ID = o.Product_ID
GROUP BY
    p.Product_ID,
    p.Product_Name
ORDER BY Quantity_Sold DESC
LIMIT 10;


-- ==========================================================

-- 7. Top 10 Products By Revenue

SELECT
    p.Product_ID,
    p.Product_Name,
    ROUND(SUM(o.Quantity * p.Price),2) AS Revenue
FROM products p
JOIN orders o
ON p.Product_ID = o.Product_ID
GROUP BY
    p.Product_ID,
    p.Product_Name
ORDER BY Revenue DESC
LIMIT 10;


-- ==========================================================

-- 8. Category Generating Highest Revenue

SELECT
    p.Category,
    ROUND(SUM(o.Quantity * p.Price),2) AS Revenue
FROM products p
JOIN orders o
ON p.Product_ID = o.Product_ID
GROUP BY p.Category
ORDER BY Revenue DESC
LIMIT 1;


-- ==========================================================

-- 9. Total Revenue

SELECT
ROUND(SUM(o.Quantity * p.Price),2) AS Total_Revenue
FROM orders o
JOIN products p
ON o.Product_ID = p.Product_ID;


-- ==========================================================

-- 10. Average Order Value

SELECT
ROUND(AVG(o.Quantity * p.Price),2) AS Average_Order_Value
FROM orders o
JOIN products p
ON o.Product_ID = p.Product_ID;


-- ==========================================================

-- 11. Monthly Revenue

SELECT
DATE_FORMAT(o.Order_Date,'%Y-%m') AS Month,
ROUND(SUM(o.Quantity * p.Price),2) AS Revenue
FROM orders o
JOIN products p
ON o.Product_ID = p.Product_ID
GROUP BY Month
ORDER BY Month;


-- ==========================================================

-- 12. Month Generating Highest Revenue

SELECT
DATE_FORMAT(o.Order_Date,'%Y-%m') AS Month,
ROUND(SUM(o.Quantity * p.Price),2) AS Revenue
FROM orders o
JOIN products p
ON o.Product_ID = p.Product_ID
GROUP BY Month
ORDER BY Revenue DESC
LIMIT 1;


-- ==========================================================

-- 13. City Generating Highest Revenue

SELECT
    c.City,
    ROUND(SUM(o.Quantity * p.Price),2) AS Revenue
FROM customers c
JOIN orders o
ON c.Customer_ID = o.Customer_ID
JOIN products p
ON o.Product_ID = p.Product_ID
GROUP BY c.City
ORDER BY Revenue DESC
LIMIT 1;


-- ==========================================================

-- 14. Most Common Payment Method

SELECT
    Payment_Method,
    COUNT(*) AS Total_Orders
FROM orders
GROUP BY Payment_Method
ORDER BY Total_Orders DESC
LIMIT 1;


-- ==========================================================

-- 15. Percentage Of Orders By Status

SELECT
    Order_Status,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM orders),
        2
    ) AS Percentage
FROM orders
GROUP BY Order_Status
ORDER BY Percentage DESC;


-- ==========================================================
-- ADVANCED ANALYSIS
-- ==========================================================

-- 16. Top 3 Customers In Every City By Revenue

WITH CustomerRevenue AS
(
SELECT

    c.City,

    c.Customer_ID,

    c.Customer_Name,

    SUM(o.Quantity*p.Price) AS Revenue,

    DENSE_RANK() OVER
    (
        PARTITION BY c.City
        ORDER BY SUM(o.Quantity*p.Price) DESC
    ) AS Ranking

FROM customers c

JOIN orders o

ON c.Customer_ID=o.Customer_ID

JOIN products p

ON o.Product_ID=p.Product_ID

GROUP BY

c.City,

c.Customer_ID,

c.Customer_Name

)

SELECT *

FROM CustomerRevenue

WHERE Ranking<=3

ORDER BY City,Ranking;


-- ==========================================================

-- 17. Highest Revenue Product In Every Category

WITH ProductRevenue AS
(
SELECT

p.Category,

p.Product_ID,

p.Product_Name,

SUM(o.Quantity*p.Price) AS Revenue,

DENSE_RANK() OVER
(
PARTITION BY p.Category
ORDER BY SUM(o.Quantity*p.Price) DESC
) Ranking

FROM products p

JOIN orders o

ON p.Product_ID=o.Product_ID

GROUP BY

p.Category,

p.Product_ID,

p.Product_Name

)

SELECT *

FROM ProductRevenue

WHERE Ranking=1;


-- ==========================================================

-- 18. Customers Spending Above Average

SELECT *
FROM
(
    SELECT
        c.Customer_ID,
        c.Customer_Name,
        SUM(o.Quantity * p.Price) AS Spending
    FROM customers c
    JOIN orders o
        ON c.Customer_ID = o.Customer_ID
    JOIN products p
        ON o.Product_ID = p.Product_ID
    GROUP BY
        c.Customer_ID,
        c.Customer_Name
) AS CustomerSpending
WHERE Spending >
(
    SELECT AVG(Spending)
    FROM
    (
        SELECT
            SUM(o.Quantity * p.Price) AS Spending
        FROM customers c
        JOIN orders o
            ON c.Customer_ID = o.Customer_ID
        JOIN products p
            ON o.Product_ID = p.Product_ID
        GROUP BY c.Customer_ID
    ) AS AvgSpend
)
ORDER BY Spending DESC
LIMIT 10;

-- ==========================================================

-- 20. Customers Purchasing From More Than 3 Categories

SELECT
    COUNT(*) AS Customers_More_Than_3_Categories
FROM (
    SELECT
        c.Customer_ID
    FROM customers c
    JOIN orders o
        ON c.Customer_ID = o.Customer_ID
    JOIN products p
        ON o.Product_ID = p.Product_ID
    GROUP BY c.Customer_ID
    HAVING COUNT(DISTINCT p.Category) > 3
) AS category_customers;
SELECT
    c.Customer_ID,
    c.Customer_Name,
    COUNT(DISTINCT p.Category) AS Categories_Purchased
FROM customers c
JOIN orders o
    ON c.Customer_ID = o.Customer_ID
JOIN products p
    ON o.Product_ID = p.Product_ID
GROUP BY
    c.Customer_ID,
    c.Customer_Name
HAVING COUNT(DISTINCT p.Category) > 3
ORDER BY
    Categories_Purchased DESC,
    c.Customer_ID
LIMIT 10;