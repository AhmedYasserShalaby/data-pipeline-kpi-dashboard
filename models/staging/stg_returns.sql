SELECT
    return_id,
    order_id,
    DATE(return_date) AS return_date,
    reason,
    refunded_amount
FROM returns
