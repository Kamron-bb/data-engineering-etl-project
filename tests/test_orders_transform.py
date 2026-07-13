from datetime import date

import pandas as pd

from src.transformations.orders_transform import (
    build_gold_daily_revenue,
    calculate_data_quality,
    transform_orders,
)


def test_transform_orders_keeps_only_valid_completed_orders():
    raw_df = pd.DataFrame(
        [
            {"order_id": 1, "customer_id": 1001, "order_date": date(2026, 1, 10), "city": "London", "amount": 100.0, "status": "completed"},
            {"order_id": 1, "customer_id": 1001, "order_date": date(2026, 1, 10), "city": "London", "amount": 100.0, "status": "completed"},
            {"order_id": 2, "customer_id": 1002, "order_date": date(2026, 1, 11), "city": "Berlin", "amount": 200.0, "status": "cancelled"},
            {"order_id": 3, "customer_id": 1003, "order_date": date(2026, 1, 12), "city": "Paris", "amount": None, "status": "completed"},
            {"order_id": 4, "customer_id": 1004, "order_date": date(2026, 1, 13), "city": "Tashkent", "amount": -50.0, "status": "completed"},
            {"order_id": 5, "customer_id": 1005, "order_date": date(2026, 1, 14), "city": None, "amount": 150.0, "status": "completed"},
            {"order_id": 6, "customer_id": 1006, "order_date": date(2026, 1, 15), "city": "", "amount": 120.0, "status": "completed"},
        ]
    )

    clean_df = transform_orders(raw_df)

    assert len(clean_df) == 1
    assert clean_df.iloc[0]["order_id"] == 1
    assert clean_df.iloc[0]["amount_with_tax"] == 120.0
    assert clean_df.iloc[0]["month"] == "2026-01"


def test_calculate_data_quality_returns_correct_metrics():
    raw_df = pd.DataFrame(
        [
            {"order_id": 1, "customer_id": 1001, "order_date": date(2026, 1, 10), "city": "London", "amount": 100.0, "status": "completed"},
            {"order_id": 1, "customer_id": 1001, "order_date": date(2026, 1, 10), "city": "London", "amount": 100.0, "status": "completed"},
            {"order_id": 2, "customer_id": 1002, "order_date": date(2026, 1, 11), "city": "Berlin", "amount": 200.0, "status": "cancelled"},
            {"order_id": 3, "customer_id": 1003, "order_date": date(2026, 1, 12), "city": "Paris", "amount": None, "status": "completed"},
            {"order_id": 4, "customer_id": 1004, "order_date": date(2026, 1, 13), "city": "Tashkent", "amount": -50.0, "status": "completed"},
            {"order_id": 5, "customer_id": 1005, "order_date": date(2026, 1, 14), "city": None, "amount": 150.0, "status": "completed"},
            {"order_id": 6, "customer_id": 1006, "order_date": date(2026, 1, 15), "city": "", "amount": 120.0, "status": "completed"},
        ]
    )

    clean_df = transform_orders(raw_df)
    dq_df = calculate_data_quality(raw_df, clean_df)
    row = dq_df.iloc[0]

    assert row["total_raw_rows"] == 7
    assert row["duplicate_order_ids"] == 1
    assert row["null_amount_count"] == 1
    assert row["negative_amount_count"] == 1
    assert row["null_city_count"] == 2
    assert row["accepted_rows"] == 1
    assert row["rejected_rows"] == 6
    assert row["data_quality_score"] == 14.29


def test_build_gold_daily_revenue_aggregates_clean_orders():
    clean_df = pd.DataFrame(
        [
            {"order_id": 1, "order_date": date(2026, 1, 10), "amount": 100.0},
            {"order_id": 2, "order_date": date(2026, 1, 10), "amount": 200.0},
            {"order_id": 3, "order_date": date(2026, 1, 11), "amount": 300.0},
        ]
    )

    gold_df = build_gold_daily_revenue(clean_df)
    first_day = gold_df[gold_df["order_date"] == date(2026, 1, 10)].iloc[0]

    assert first_day["total_orders"] == 2
    assert first_day["total_revenue"] == 300.0
    assert first_day["avg_order_value"] == 150.0