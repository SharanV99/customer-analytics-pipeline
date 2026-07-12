# Project Notes

## Cleaning decisions (from data exploration)

1. Remove cancelled transactions — invoices starting with "C".
   Reason: these are returns/cancellations, not sales. Including them
   would distort every customer's frequency and monetary totals.

2. Remove rows with null Customer ID (~243,008 rows, ~23% of data).
   Reason: this is a customer-level analysis (RFM, cohorts, retention);
   a transaction with no customer can't be attributed to a segment.
   Note: large share — for a pure revenue-total analysis they'd be handled differently.

3. Keep only rows where quantity > 0 AND price > 0.
   Reason: negatives/zeros are returns, accounting adjustments
   (min price was -53,594.36), and free items — not genuine sales.

## Key facts from exploration
- 1,067,372 rows, 8 columns
- 5,942 distinct customers
- Price range: -53,594.36 to 38,970.0
