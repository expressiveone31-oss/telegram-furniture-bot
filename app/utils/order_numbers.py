from datetime import datetime


def generate_order_number() -> str:
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    suffix = f"{now.microsecond:06d}"
    return f"ORD-{date_str}-{suffix}"
