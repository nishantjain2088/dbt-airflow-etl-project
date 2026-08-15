with orders as (
    select * from {{ ref('stg_orders') }}
),
items as (
    select * from {{ source('raw_source', 'order_items') }}
)

select
    cast(orders.order_timestamp as date) as sales_date,
    orders.order_status,
    count(distinct orders.order_id) as total_orders,
    round(sum(items.quantity * items.item_price), 2) as gross_revenue
from orders
left join items on orders.order_id = items.order_id
group by 1, 2
order by sales_date desc
