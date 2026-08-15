with source as (
    select * from {{ source('raw_source', 'orders') }}
),
deduped as (
    select
        order_id,
        user_id,
        order_timestamp,
        status,
        row_number() over (partition by order_id order by order_timestamp desc) as rn
    from source
)
select 
    order_id,
    user_id,
    order_timestamp,
    upper(status) as order_status
from deduped 
where rn = 1
