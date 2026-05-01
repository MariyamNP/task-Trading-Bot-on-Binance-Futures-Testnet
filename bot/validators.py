from decimal import Decimal, InvalidOperation

VALID_SIDES = {'BUY', 'SELL'}
VALID_ORDER_TYPES = {'MARKET', 'LIMIT', 'STOP'}


def validate_symbol(symbol):
    symbol = symbol.strip().upper()
    if not symbol or not symbol.isalpha():
        raise ValueError(f"Invalid symbol '{symbol}'. Example: BTCUSDT")
    return symbol


def validate_side(side):
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Side must be one of {VALID_SIDES}, got '{side}'")
    return side


def validate_order_type(order_type):
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(f"Order type must be one of {VALID_ORDER_TYPES}, got '{order_type}'")
    return order_type


def validate_quantity(quantity):
    try:
        qty = Decimal(str(quantity))
        if qty <= 0:
            raise ValueError('Quantity must be greater than 0')
        return str(qty)
    except InvalidOperation:
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a positive number.")


def validate_price(price):
    try:
        p = Decimal(str(price))
        if p <= 0:
            raise ValueError('Price must be greater than 0')
        return str(p)
    except InvalidOperation:
        raise ValueError(f"Invalid price '{price}'. Must be a positive number.")


def validate_order_params(symbol, side, order_type, quantity, price=None, stop_price=None):
    validated = {
        'symbol':   validate_symbol(symbol),
        'side':     validate_side(side),
        'type':     validate_order_type(order_type),
        'quantity': validate_quantity(quantity),
    }
    if validated['type'] == 'LIMIT':
        if price is None:
            raise ValueError('Price is required for LIMIT orders.')
        validated['price'] = validate_price(price)
    if validated['type'] == 'STOP':
        if price is None:
            raise ValueError('Limit price is required for STOP orders.')
        if stop_price is None:
            raise ValueError('stop_price is required for STOP orders.')
        validated['price']     = validate_price(price)
        validated['stopPrice'] = validate_price(stop_price)
    return validated
