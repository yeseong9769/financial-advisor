#!/usr/bin/env python3
"""
Market Data Fetcher with Caching

Fetches market data from Yahoo Finance via yfinance library.
Implements file-based caching to reduce repeated network calls.

Usage:
    python market_data_fetcher.py --symbol AAPL --endpoint quote
    python market_data_fetcher.py --symbol AAPL --endpoint overview --format json
    echo '{"symbol": "AAPL", "endpoint": "quote"}' | python market_data_fetcher.py --stdin

Endpoints:
    quote       -> Current price/change/volume (cache: 5 min)
    overview    -> Company fundamentals (cache: 1 day)
    income      -> Income statement (cache: 1 day)
    balance     -> Balance sheet (cache: 1 day)
    cashflow    -> Cash flow statement (cache: 1 day)
    daily       -> Daily OHLCV time series (cache: 1 hour)
    news        -> News articles (cache: 30 min)
"""

import argparse
import hashlib
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

CACHE_DIR = Path.home() / ".cache" / "financial-advisor"
CACHE_TTL = {
    "quote": 300,
    "daily": 3600,
    "overview": 86400,
    "income": 86400,
    "balance": 86400,
    "cashflow": 86400,
    "news": 1800,
}


def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_key(symbol: str, endpoint: str) -> str:
    key = f"{symbol.upper()}_{endpoint}"
    return hashlib.md5(key.encode()).hexdigest()


def _get_cache_path(symbol: str, endpoint: str) -> Path:
    _ensure_cache_dir()
    cache_key = _get_cache_key(symbol, endpoint)
    return CACHE_DIR / f"{cache_key}.json"


def _is_cache_valid(cache_path: Path, endpoint: str) -> bool:
    if not cache_path.exists():
        return False
    ttl = CACHE_TTL.get(endpoint, 3600)
    mtime = cache_path.stat().st_mtime
    age = time.time() - mtime
    return age < ttl


def _read_cache(cache_path: Path) -> Optional[Dict[str, Any]]:
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _write_cache(cache_path: Path, data: Dict[str, Any]) -> None:
    try:
        with open(cache_path, 'w') as f:
            json.dump(data, f)
    except IOError:
        pass


def _clean(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
    return obj


def _fetch_yahoo_finance(symbol: str, endpoint: str) -> Optional[Dict[str, Any]]:
    import yfinance as yf

    try:
        ticker = yf.Ticker(symbol)
    except Exception:
        return None

    try:
        if endpoint == "quote":
            info = ticker.fast_info
            return _clean({
                "symbol": symbol.upper(),
                "name": info.get("longName") or symbol.upper(),
                "price": info.get("lastPrice") or info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "changePercent": info.get("regularMarketChangePercent"),
                "volume": info.get("regularMarketVolume"),
                "marketCap": info.get("marketCap"),
                "peRatio": info.get("trailingPE") or info.get("forwardPE"),
                "dayHigh": info.get("dayHigh"),
                "dayLow": info.get("dayLow"),
                "previousClose": info.get("regularMarketPreviousClose"),
                "open": info.get("regularMarketOpen"),
            })

        if endpoint == "daily":
            hist = ticker.history(period="1y")
            if hist.empty:
                return None
            time_series = {}
            for date, row in hist.iterrows():
                ds = date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date)
                time_series[ds] = {
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": int(row["Volume"]),
                }
            return _clean({"Time Series (Daily)": time_series})

        if endpoint == "overview":
            info = ticker.info
            fields = {
                "symbol": "symbol", "name": "shortName", "sector": "sector",
                "industry": "industry", "marketCap": "marketCap",
                "enterpriseValue": "enterpriseValue",
                "trailingPE": "trailingPE", "forwardPE": "forwardPE",
                "priceToBook": "priceToBook", "priceToSalesTrailing12Months": "priceToSalesTrailing12Months",
                "enterpriseToEbitda": "enterpriseToEbitda", "enterpriseToRevenue": "enterpriseToRevenue",
                "dividendYield": "dividendYield", "dividendRate": "dividendRate", "payoutRatio": "payoutRatio",
                "beta": "beta", "peRatio": "trailingPE",
                "eps": "trailingEps", "earningsPerShare": "trailingEps",
                "revenue": "totalRevenue", "revenuePerShare": "revenuePerShare",
                "grossProfit": "grossProfit", "ebitda": "ebitda",
                "profitMargins": "profitMargins", "grossMargins": "grossMargins",
                "operatingMargins": "operatingMargins",
                "returnOnEquity": "returnOnEquity", "returnOnAssets": "returnOnAssets",
                "debtToEquity": "debtToEquity", "currentRatio": "currentRatio", "quickRatio": "quickRatio",
                "totalDebt": "totalDebt", "totalCash": "totalCash",
                "freeCashflow": "freeCashflow", "operatingCashflow": "operatingCashflow",
                "revenueGrowth": "revenueGrowth", "earningsGrowth": "earningsGrowth",
                "bookValue": "bookValue",
                "52WeekHigh": "fiftyTwoWeekHigh", "52WeekLow": "fiftyTwoWeekLow",
                "50DayAverage": "fiftyDayAverage", "200DayAverage": "twoHundredDayAverage",
                "targetMeanPrice": "targetMeanPrice", "recommendationMean": "recommendationMean",
                "recommendationKey": "recommendationKey",
                "numberOfAnalystOpinions": "numberOfAnalystOpinions",
                "exDividendDate": "exDividendDate", "dividendDate": "dividendDate",
                "sharesOutstanding": "sharesOutstanding", "floatShares": "floatShares",
                "country": "country", "website": "website", "longBusinessSummary": "longBusinessSummary",
            }
            result = {}
            for our_key, yf_key in fields.items():
                result[our_key] = info.get(yf_key)
            return _clean(result)

if endpoint in ("income", "balance", "cashflow"):
            stmt_map = {
                "income": ticker.income_stmt,
                "balance": ticker.balance_sheet,
                "cashflow": ticker.cashflow,
            }
            stmt = stmt_map[endpoint]
            if stmt is None or stmt.empty:
                return None
            result = {}
            for date in stmt.columns:
                ds = date.strftime("%Y-%m-%d") if hasattr(date, 'strftime') else str(date)
                result[ds] = {}
                for item in stmt.index:
                    try:
                        val = stmt.loc[item, date]
                        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                            continue
                        result[ds][item] = val
                    except Exception:
                        pass

            latest_date = stmt.columns[0]
            latest_ds = latest_date.strftime("%Y-%m-%d") if hasattr(latest_date, 'strftime') else str(latest_date)
            latest = result[latest_ds]

            if endpoint == "income":
                result["_latest"] = {
                    "revenue": latest.get("Total Revenue"),
                    "cost_of_goods_sold": latest.get("Cost Of Revenue"),
                    "operating_income": latest.get("Operating Income") or latest.get("EBIT"),
                    "net_income": latest.get("Net Income"),
                    "interest_expense": latest.get("Interest Expense"),
                    "ebitda": latest.get("EBITDA"),
                }
            elif endpoint == "balance":
                result["_latest"] = {
                    "total_assets": latest.get("Total Assets"),
                    "total_equity": latest.get("Stockholders Equity") or latest.get("Total Equity Gross Minority Interest"),
                    "current_assets": latest.get("Current Assets"),
                    "current_liabilities": latest.get("Current Liabilities"),
                    "total_debt": latest.get("Total Debt"),
                    "cash_and_equivalents": latest.get("Cash And Cash Equivalents") or latest.get("Cash"),
                    "inventory": latest.get("Inventory"),
                    "accounts_receivable": latest.get("Accounts Receivable") or latest.get("Net Receivables"),
                }
            elif endpoint == "cashflow":
                result["_latest"] = {
                    "operating_cash_flow": latest.get("Operating Cash Flow") or latest.get("Cash From Operating Activities"),
                    "total_debt_service": latest.get("Interest Paid") or latest.get("Interest Expense"),
                }

            return result

if endpoint == "news":
            news = ticker.news
            if not news:
                return None
            items = []
            for article in news[:20]:
                ts = article.get("providerPublishTime")
                published = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else None
                items.append({
                    "title": article.get("title"),
                    "source": article.get("publisher"),
                    "published": published,
                    "summary": article.get("summary"),
                    "link": article.get("link"),
                    "type": article.get("type"),
                })
            return _clean({"news": items})

    except Exception:
        pass

    return None


def fetch_market_data(
    symbol: str,
    endpoint: str,
    use_cache: bool = True,
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Fetch market data with caching.

    Returns:
        Tuple of (data_dict, source_string)
        source_string: "cache", "yahoo_finance", or "error"
    """
    cache_path = _get_cache_path(symbol, endpoint)

    if use_cache and _is_cache_valid(cache_path, endpoint):
        cached_data = _read_cache(cache_path)
        if cached_data:
            cached_data["_cached"] = True
            return cached_data, "cache"

    yahoo_data = _fetch_yahoo_finance(symbol, endpoint)
    if yahoo_data:
        yahoo_data["_source"] = "yahoo_finance"
        yahoo_data["_cached"] = False
        if use_cache:
            _write_cache(cache_path, yahoo_data)
        return yahoo_data, "yahoo_finance"

    return None, "error"


def clear_cache(symbol: Optional[str] = None, endpoint: Optional[str] = None) -> int:
    if not CACHE_DIR.exists():
        return 0

    deleted = 0
    for cache_file in CACHE_DIR.glob("*.json"):
        if symbol and endpoint:
            expected_key = _get_cache_key(symbol, endpoint)
            if cache_file.stem == expected_key:
                cache_file.unlink()
                deleted += 1
        else:
            cache_file.unlink()
            deleted += 1
    return deleted


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch market data with caching"
    )
    parser.add_argument("--symbol", required=True, help="Stock symbol (e.g., AAPL)")
    parser.add_argument(
        "--endpoint",
        required=True,
        choices=["quote", "overview", "income", "balance", "cashflow", "daily", "news"],
        help="Data endpoint to fetch"
    )
    parser.add_argument("--format", choices=["text", "json"], default="json")
    parser.add_argument("--no-cache", action="store_true", help="Skip cache, force fresh fetch")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache for this symbol/endpoint")
    parser.add_argument("--stdin", action="store_true", help="Read parameters from stdin as JSON")

    args = parser.parse_args()

    if args.stdin:
        try:
            stdin_data = json.load(sys.stdin)
            args.symbol = stdin_data.get("symbol", args.symbol)
            args.endpoint = stdin_data.get("endpoint", args.endpoint)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON from stdin: {e}", file=sys.stderr)
            sys.exit(1)

        if not args.symbol or not args.endpoint:
            print("Error: stdin JSON must contain 'symbol' and 'endpoint'", file=sys.stderr)
            sys.exit(1)

    if args.clear_cache:
        deleted = clear_cache(args.symbol, args.endpoint)
        print(f"Cleared {deleted} cache file(s)")
        sys.exit(0)

    data, source = fetch_market_data(
        symbol=args.symbol,
        endpoint=args.endpoint,
        use_cache=not args.no_cache,
    )

    if data is None:
        print(f"Error: Failed to fetch data for {args.symbol} ({args.endpoint})", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        output = {
            "data": data,
            "source": source,
            "symbol": args.symbol,
            "endpoint": args.endpoint,
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Symbol: {args.symbol}")
        print(f"Endpoint: {args.endpoint}")
        print(f"Source: {source}")
        print(f"Data: {json.dumps(data, indent=2)}")


if __name__ == "__main__":
    main()