{{ config(materialized='table') }}

with customer_cohort as (

    -- step 1: each customer's cohort = month of their first purchase
    select
        customer_id,
        date_trunc('month', min(invoice_date)) as cohort_month
    from stg_transactions
    group by customer_id

),

customer_activity as (

    -- step 2: for every purchase, find which month it happened in
    select distinct
        customer_id,
        date_trunc('month', invoice_date) as activity_month
    from stg_transactions

),

cohort_offsets as (

    -- step 3: join cohort to activity, compute months-since-first-purchase
    select
        c.cohort_month,
        a.customer_id,
        date_diff('month', c.cohort_month, a.activity_month) as month_offset
    from customer_cohort c
    join customer_activity a on c.customer_id = a.customer_id

)

-- final: count distinct customers per cohort per offset
select
    cohort_month,
    month_offset,
    count(distinct customer_id) as active_customers
from cohort_offsets
group by cohort_month, month_offset
order by cohort_month, month_offset