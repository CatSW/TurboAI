<<<FILE path="src/order_service.py" bytes="120">>>
from discount_rules import apply_discount


def total(price: float, tier: str) -> float:
    return apply_discount(price, tier)
<<<END FILE>>>
