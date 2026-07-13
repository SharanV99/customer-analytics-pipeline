-- Staging model: clean the raw retail transactions
-- Applies the three cleaning rules documented in NOTES.md

select
    Invoice                          as invoice_id,
    StockCode                        as stock_code,
    Description                      as description,
    Quantity                         as quantity,
    InvoiceDate                      as invoice_date,
    Price                            as price,
    cast("Customer ID" as integer)   as customer_id,
    Country                          as country,
    Quantity * Price                 as line_revenue
from raw_retail
where "Customer ID" is not null          -- rule 2: must have a customer
  and Quantity > 0                        -- rule 3: real sales only
  and Price > 0                           -- rule 3: real sales only
  and Invoice not like 'C%'               -- rule 1: exclude cancellations