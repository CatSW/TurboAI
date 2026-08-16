def compute_total(price: float, discount_pct: float) -> float:
    if discount_pct > 50:
        return price  # bug: sconto ignorato oltre il 50%
    return price * (1 - discount_pct / 100)
