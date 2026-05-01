import logging
from bot.validators import validate_order_params

logger = logging.getLogger('trading_bot.orders')

def _build_order_params(symbol, side, order_type, quantity, price=None, stop_price=None):
    validated = validate_order_params(symbol, side, order_type, quantity, price, stop_price)
    params = {
        'symbol':   validated['symbol'],
        'side':     validated['side'],
        'type':     validated['type'],
        'quantity': validated['quantity'],
    }
    if order_type == 'LIMIT':
        params['price']       = validated['price']
        params['timeInForce'] = 'GTC'
    if order_type == 'STOP':
        params['price']       = validated['price']
        params['stopPrice']   = validated['stopPrice']
        params['timeInForce'] = 'GTC'
    return params

def print_order_summary(params):
    print('\n' + '=' * 50)
    print('  ORDER REQUEST SUMMARY')
    print('=' * 50)
    for label, key in [('Symbol','symbol'),('Side','side'),('Type','type'),
                        ('Quantity','quantity'),('Price','price'),('Stop Price','stopPrice')]:
        if key in params:
            print(f'  {label:<12}: {params[key]}')
    print('=' * 50 + '\n')

def print_order_response(response):
    print('\n' + '=' * 50)
    print('  ORDER RESPONSE')
    print('=' * 50)
    print(f"  Order ID     : {response.get('orderId')}")
    print(f"  Symbol       : {response.get('symbol')}")
    print(f"  Side         : {response.get('side')}")
    print(f"  Type         : {response.get('type')}")
    print(f"  Status       : {response.get('status')}")
    print(f"  Orig Qty     : {response.get('origQty')}")
    print(f"  Executed Qty : {response.get('executedQty')}")
    print(f"  Avg Price    : {response.get('avgPrice') or response.get('price','N/A')}")
    print('=' * 50 + '\n')

def place_order(client, symbol, side, order_type, quantity, price=None, stop_price=None):
    params = _build_order_params(symbol, side, order_type, quantity, price, stop_price)
    print_order_summary(params)
    logger.info('Submitting %s %s: symbol=%s qty=%s price=%s stop_price=%s',
                order_type, side, symbol, quantity, price or 'N/A', stop_price or 'N/A')
    try:
        response = client.place_order(params)
        logger.info('Order placed. orderId=%s status=%s', response.get('orderId'), response.get('status'))
        print_order_response(response)
        print('Order placed successfully!')
        return response
    except Exception as exc:
        logger.error('Order failed: %s', exc)
        print(f'Order failed: {exc}')
        raise
