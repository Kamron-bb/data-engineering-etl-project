from datetime import date

import pandas as pd


def transform_orders(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean raw orders and prepare silver analytical layer.
    """
    clean_df = raw_df.copy()

    clean_df = clean_df.drop_duplicates(subset=["order_id"])
    clean_df = clean_df[clean_df["amount"].notna()]
    clean_df = clean_df[clean_df["amount"] > 0]
    clean_df = clean_df[clean_df["city"].notna()]
    clean_df = clean_df[clean_df["city"] != ""]
    clean_df = clean_df[clean_df["status"] == "completed"]

    clean_df["amount_with_tax"] = (clean_df["amount"] * 1.2).round(2)
    clean_df["month"] = pd.to_datetime(clean_df["order_date"]).dt.strftime("%Y-%m")

    return clean_df


def calculate_data_quality(raw_df: pd.DataFrame, clean_df: pd.DataFrame) -> pd.DataFrame:
    total_raw_rows = len(raw_df)
    duplicate_order_ids = raw_df.duplicated(subset=["order_id"]).sum()
    null_amount_count = raw_df["amount"].isna().sum()
    negative_amount_count = (raw_df["amount"].fillna(0) < 0).sum()
    null_city_count = raw_df["city"].isna().sum() + (raw_df["city"] == "").sum()

    accepted_rows = len(clean_df)
    rejected_rows = total_raw_rows - accepted_rows

    data_quality_score = round((accepted_rows / total_raw_rows) * 100, 2) if total_raw_rows else 0

    return pd.DataFrame(
        [
            {
                "check_date": date.today(),
                "total_raw_rows": total_raw_rows,
                "duplicate_order_ids": int(duplicate_order_ids),
                "null_amount_count": int(null_amount_count),
                "negative_amount_count": int(negative_amount_count),
                "null_city_count": int(null_city_count),
                "accepted_rows": accepted_rows,
                "rejected_rows": rejected_rows,
                "data_quality_score": data_quality_score,
            }
        ]
    )


def build_gold_daily_revenue(clean_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build business-ready gold table for reporting.
    """
    if clean_df.empty:
        return pd.DataFrame(
            columns=[
                "order_date",
                "total_orders",
                "total_revenue",
                "avg_order_value",
            ]
        )

    gold_df = (
        clean_df.groupby("order_date")
        .agg(
            total_orders=("order_id", "count"),
            total_revenue=("amount", "sum"),
            avg_order_value=("amount", "mean"),
        )
        .reset_index()
    )

    gold_df["total_revenue"] = gold_df["total_revenue"].round(2)
    gold_df["avg_order_value"] = gold_df["avg_order_value"].round(2)

    return gold_df
