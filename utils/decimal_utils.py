import decimal
from decimal import Decimal, getcontext
from typing import List

getcontext().prec = 28

def format_decimal(value: Decimal, precision: int = 0, rounding: str = decimal.ROUND_DOWN) -> Decimal:
    if not isinstance(value, Decimal):
        try:
            value = Decimal(str(value))
        except (ValueError, TypeError) as error:
            raise ValueError(f"Cannot format non-decimal value: {value}")

    if precision <= 0:
        return value.to_integral_exact(rounding=getattr(decimal, rounding))
    else:
        quantizer = Decimal('0.' + '0' * precision)
        return value.quantize(quantizer, rounding=getattr(decimal, rounding))


def decimal_sum(values: List, default: Decimal = Decimal('0')) -> Decimal:
    if not values:
        return default
    try:
        decimal_values = [Decimal(str(value)) if not isinstance(value, Decimal) else value for value in values]
        return sum(decimal_values, Decimal('0'))
    except Exception as error:
        raise ValueError(f"Cannot calculate sum of values: {error}")
