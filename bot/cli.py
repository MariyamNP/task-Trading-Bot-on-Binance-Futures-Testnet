"""
cli.py  —  Command-Line Interface for the Binance Futures Testnet Trading Bot.

Usage examples
--------------
# Market BUY
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit SELL
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000

# Stop-Market BUY
python cli.py --symbol BTCUSDT --side BUY --type STOP_MARKET --quantity 0.001 --price 95000

# Check account balance
python cli.py --account

# Using environment variables for keys (recommended):
# export BINANCE_API_KEY=your_key
# export BINANCE_API_SECRET=your_secret
"""

import argparse
import json
import os
import sys

from bot.client import BinanceClient
from bot.logging_config import setup_logging
from bot.orders import place_order


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_credentials() -> tuple[str, str]:
    """
    Read API credentials from environment variables.
    Falls back to prompting the user interactively.
    """
    api_key = os.environ.get("BINANCE_API_KEY", "").strip()
    api_secret = os.environ.get("BINANCE_API_SECRET", "").strip()

    if not api_key:
        api_key = input("Enter your Binance Testnet API Key: ").strip()
    if not api_secret:
        api_secret = input("Enter your Binance Testnet API Secret: ").strip()

    if not api_key or not api_secret:
        print("❌  API key and secret are required.")
        sys.exit(1)

    return api_key, api_secret


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.001
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.001 --price 100000
  python cli.py --account
  python cli.py --open-orders BTCUSDT
        """,
    )

    # --- Credentials (optional; falls back to env vars or interactive prompt) ---
    parser.add_argument("--api-key",    help="Binance API key    (or set BINANCE_API_KEY env var)")
    parser.add_argument("--api-secret", help="Binance API secret (or set BINANCE_API_SECRET env var)")

    # --- Order parameters ---
    order_group = parser.add_argument_group("Order parameters")
    order_group.add_argument("--symbol",   type=str, help="Trading pair, e.g. BTCUSDT")
    order_group.add_argument("--side",     type=str, choices=["BUY", "SELL"], help="Order side")
    order_group.add_argument("--type",     type=str, dest="order_type",
                             choices=["MARKET", "LIMIT", "STOP_MARKET"], help="Order type")
    order_group.add_argument("--quantity", type=str, help="Order quantity (base asset)")
    order_group.add_argument("--price",    type=str, default=None,
                             help="Limit price (required for LIMIT / stop price for STOP_MARKET)")

    # --- Utility flags ---
    util_group = parser.add_argument_group("Utility commands")
    util_group.add_argument("--account",     action="store_true", help="Print account info and exit")
    util_group.add_argument("--open-orders", metavar="SYMBOL",    help="List open orders for a symbol and exit")
    util_group.add_argument("--server-time", action="store_true", help="Print server time and exit")

    # --- Logging ---
    parser.add_argument("--log-file", default="trading_bot.log", help="Log file path (default: trading_bot.log)")
    parser.add_argument("--verbose",  action="store_true",        help="Also print DEBUG logs to console")

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = build_parser()
    args = parser.parse_args()

    # --- Logging setup ---
    import logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_file=args.log_file, level=log_level)

    import logging as _log
    logger = _log.getLogger("trading_bot.cli")
    logger.info("CLI started with args: %s", vars(args))

    # --- Credentials ---
    if args.api_key:
        os.environ["BINANCE_API_KEY"] = args.api_key
    if args.api_secret:
        os.environ["BINANCE_API_SECRET"] = args.api_secret

    api_key, api_secret = get_credentials()
    client = BinanceClient(api_key=api_key, api_secret=api_secret)

    # -------------------------------------------------------------------
    # Utility commands
    # -------------------------------------------------------------------

    if args.server_time:
        result = client.get_server_time()
        print(f"Server time (ms): {result.get('serverTime')}")
        return

    if args.account:
        print("\nFetching account info …")
        try:
            info = client.get_account_info()
            print(f"\nTotal Wallet Balance : {info.get('totalWalletBalance')} USDT")
            print(f"Available Balance    : {info.get('availableBalance')} USDT")
            print(f"Total Unrealised PnL : {info.get('totalUnrealizedProfit')} USDT")
        except Exception as exc:
            print(f"❌  Could not fetch account info: {exc}")
            sys.exit(1)
        return

    if args.open_orders:
        print(f"\nFetching open orders for {args.open_orders} …")
        try:
            orders = client.get_open_orders(symbol=args.open_orders.upper())
            if not orders:
                print("No open orders.")
            else:
                for o in orders:
                    print(json.dumps(o, indent=2))
        except Exception as exc:
            print(f"❌  Could not fetch open orders: {exc}")
            sys.exit(1)
        return

    # -------------------------------------------------------------------
    # Order placement
    # -------------------------------------------------------------------

    # Validate that required order arguments are present
    missing = [f"--{f}" for f, v in [("symbol", args.symbol), ("side", args.side),
                                       ("type", args.order_type), ("quantity", args.quantity)] if not v]
    if missing:
        parser.error(f"The following arguments are required for placing an order: {', '.join(missing)}")

    try:
        place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
    except ValueError as exc:
        print(f"\n❌  Validation error: {exc}\n")
        logger.error("Validation error: %s", exc)
        sys.exit(1)
    except Exception as exc:
        print(f"\n❌  Order failed: {exc}\n")
        logger.error("Order failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
