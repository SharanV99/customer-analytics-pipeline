{{ config(materialized='table') }}

with customer_rfm as (

    select
        customer_id,
        count(distinct invoice_id)                          as frequency,
        sum(line_revenue)                                   as monetary,
        date_diff('day', max(invoice_date),
                  (select max(invoice_date) from stg_transactions)) as recency
    from stg_transactions
    group by customer_id

),

scored as (

    select
        customer_id,
        recency,
        frequency,
        monetary,
        ntile(5) over (order by recency desc)   as r_score,
        ntile(5) over (order by frequency asc)  as f_score,
        ntile(5) over (order by monetary asc)   as m_score
    from customer_rfm

)

select
    customer_id,
    recency,
    frequency,
    monetary,
    r_score,
    f_score,
    m_score,
    case
        when r_score >= 4 and f_score >= 4 then 'Champions'
        when f_score >= 4                  then 'Loyal'
        when r_score >= 4 and f_score <= 2 then 'New'
        when r_score <= 2 and f_score >= 3 then 'At Risk'
        else 'Lost / Hibernating'
    end as segment
from scored