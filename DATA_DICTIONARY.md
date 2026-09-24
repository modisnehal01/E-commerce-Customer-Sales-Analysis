# Data dictionary and calculation definitions

All records are synthetic. Dates are formatted YYYY-MM-DD and currencies are GBP.

## Source tables

**raw_customers.csv** (grain: one customer ID)
- `customer_id`: numeric join key.
- `customer_code`: fictional, non-identifying display code.
- `region`: North, South, Midlands, Scotland or Wales; some blank/mixed-case values intentionally included.
- `signup_date`: synthetic customer signup date; **not** the cohort date.

**raw_products.csv** (grain: one product ID)
- `product_id`: numeric join key.
- `product_name`: product label.
- `category`: Electronics, Home Office, Accessories or Stationery.
- `list_price_gbp`: reference sales price, not used to recognise revenue.
- `unit_cost_gbp`: reference cost; reporting uses the order-line transaction cost snapshot.

**raw_orders.csv** (grain: one order ID, before intentional duplicate)
- `order_id`: unique business key after deduplication.
- `customer_id`: foreign key to customers.
- `order_date`: synthetic calendar date.
- `status`: Completed, Cancelled or Returned, normalised by trimming/case conversion.

**raw_order_items.csv** (grain: one line ID, before intentional duplicates)
- `order_item_id`: unique line key after deduplication.
- `order_id`: foreign key to orders.
- `product_id`: foreign key to products.
- `quantity`: positive ordered units.
- `unit_price_gbp`: selling price snapshot before discount.
- `unit_cost_gbp`: transaction cost snapshot.
- `discount_pct`: numeric fraction, e.g. 0.10 for 10%.

## Reporting definitions

- Completed-order net revenue = sum(`quantity * unit_price_gbp * (1 - discount_pct)`).
- COGS = sum(`quantity * unit_cost_gbp`) for completed orders.
- Gross profit = net revenue - COGS.
- Gross margin (%) = 100 × aggregate gross profit / aggregate net revenue.
- Completed orders = distinct completed `order_id` after data-quality filtering.
- Active customers = distinct customers with >=1 completed order in the reporting period.
- Average order value = aggregate net revenue / number of completed orders.
- RFM recency = days from latest completed purchase to 2026-08-31; frequency = distinct completed order count within observation period; monetary = completed-order net revenue.
- Cohort month = first observed completed order month, not signup month or lifetime first purchase. Month-0 retention is 100%; months not yet elapsed are blank.
- 2026 ends 2026-08-31. Compare January–August across years, not to full 2024 or 2025.
