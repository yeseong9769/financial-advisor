#!/usr/bin/env python3
"""
Market Data Fetcher with Caching and Rate Limiting

Fetches market data from Alpha Vantage (primary) and Yahoo Finance (fallback).
Implements file-based caching and rate limiting to avoid API throttling.

Usage:
    python market_data_fetcher.py --symbol AAPL --endpoint quote
    python market_data_fetcher.py --symbol AAPL --endpoint overview --format json
    echo '{"symbol": "AAPL", "endpoint": "quote"}' | python market_data_fetcher.py --stdin

Endpoints:
    quote       -> GLOBAL_QUOTE (cache: 5 min)
    overview    -> COMPANY_OVERVIEW (cache: 1 day)
    income      -> INCOME_STATEMENT (cache: 1 day)
    balance     -> BALANCE_SHEET (cache: 1 day)
    cashflow    -> CASH_FLOW (cache: 1 day)
    daily       -> TIME_SERIES_DAILY (cache: 1 hour)
    news        -> NEWS_SENTIMENT (cache: 30 min)
"""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Cache configuration
CACHE_DIR = Path.home() / ".cache" / "financial-advisor"
CACHE_TTL = {
    "quote": 300,       # 5 minutes for price quotes
    "daily": 3600,      # 1 hour for daily prices
    "overview": 86400,  # 1 day for company fundamentals
    "income": 86400,    # 1 day for financial statements
    "balance": 86400,
    "cashflow": 86400,
    "news": 1800,       # 30 minutes for news
}

# Rate limiting
ALPHA_VANTAGE_CALLS_PER_MINUTE = 5
ALPHA_VANTAGE_MIN_INTERVAL = 60.0 / ALPHA_VANTAGE_CALLS_PER_MINUTE  # 12 seconds
RATE_LIMIT_FILE = CACHE_DIR / ".av_last_call"


def _ensure_cache_dir() -> None:
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_key(symbol: str, endpoint: str) -> str:
    """Generate cache file key from symbol and endpoint."""
    key = f"{symbol.upper()}_{endpoint}"
    return hashlib.md5(key.encode()).hexdigest()


def _get_cache_path(symbol: str, endpoint: str) -> Path:
    """Get cache file path."""
    _ensure_cache_dir()
    cache_key = _get_cache_key(symbol, endpoint)
    return CACHE_DIR / f"{cache_key}.json"


def _is_cache_valid(cache_path: Path, endpoint: str) -> bool:
    """Check if cached data is still valid based on TTL."""
    if not cache_path.exists():
        return False
    
    ttl = CACHE_TTL.get(endpoint, 3600)
    mtime = cache_path.stat().st_mtime
    age = time.time() - mtime
    
    return age < ttl


def _read_cache(cache_path: Path) -> Optional[Dict[str, Any]]:
    """Read cached data."""
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def _write_cache(cache_path: Path, data: Dict[str, Any]) -> None:
    """Write data to cache."""
    try:
        with open(cache_path, 'w') as f:
            json.dump(data, f)
    except IOError:
        pass  # Fail silently on cache write errors


def _wait_for_rate_limit() -> None:
    """Wait if needed to respect Alpha Vantage rate limit."""
    if not RATE_LIMIT_FILE.exists():
        return
    
    try:
        with open(RATE_LIMIT_FILE, 'r') as f:
            last_call = float(f.read().strip())
        
        elapsed = time.time() - last_call
        if elapsed < ALPHA_VANTAGE_MIN_INTERVAL:
            sleep_time = ALPHA_VANTAGE_MIN_INTERVAL - elapsed
            time.sleep(sleep_time)
    except (ValueError, IOError):
        pass


def _update_rate_limit() -> None:
    """Update rate limit timestamp."""
    try:
        with open(RATE_LIMIT_FILE, 'w') as f:
            f.write(str(time.time()))
    except IOError:
        pass


def _fetch_yahoo_finance(symbol: str, endpoint: str) -> Optional[Dict[str, Any]]:
    """
    Fetch data from Yahoo Finance as fallback.
    
    Yahoo Finance has different endpoints, so we map Alpha Vantage endpoints
    to Yahoo Finance equivalents where possible.
    """
    # Map Korean exchange suffixes to Yahoo Finance format (no suffix)
    yahoo_symbol = symbol.replace('.KS', '').replace('.KQ', '')
    
    try:
        if endpoint == "quote":
            # Yahoo Finance quote summary
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?interval=1d&range=1d"
            req = Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    meta = result['meta']
                    quote = result['indicators']['quote'][0]
                    
                    # Get latest price
                    close_prices = quote.get('close', [])
                    if close_prices and close_prices[-1] is not None:
                        current_price = close_prices[-1]
                        prev_close = meta.get('previousClose', current_price)
                        change = current_price - prev_close
                        change_pct = (change / prev_close * 100) if prev_close else 0
                        
                        return {
                            "Global Quote": {
                                "01. symbol": symbol,
                                "02. open": str(quote.get('open', [0])[-1] or 0),
                                "03. high": str(quote.get('high', [0])[-1] or 0),
                                "04. low": str(quote.get('low', [0])[-1] or 0),
                                "05. price": str(current_price),
                                "06. volume": str(quote.get('volume', [0])[-1] or 0),
                                "07. latest trading day": datetime.now().strftime("%Y-%m-%d"),
                                "08. previous close": str(prev_close),
                                "09. change": str(change),
                                "10. change percent": f"{change_pct:.2f}%"
                            },
                            "_source": "yahoo_finance",
                            "_cached": False
                        }
        
        elif endpoint == "daily":
            # Yahoo Finance historical data
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}?interval=1d&range=1y"
            req = Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    timestamps = result['timestamp']
                    quote = result['indicators']['quote'][0]
                    
                    time_series = {}
                    for i, ts in enumerate(timestamps):
                        if all(v is not None for v in [quote['open'][i], quote['high'][i], quote['low'][i], quote['close'][i], quote['volume'][i]]):
                            date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                            time_series[date_str] = {
                                "1. open": str(quote['open'][i]),
                                "2. high": str(quote['high'][i]),
                                "3. low": str(quote['low'][i]),
                                "4. close": str(quote['close'][i]),
                                "5. volume": str(quote['volume'][i])
                            }
                    
                    return {
                        "Time Series (Daily)": time_series,
                        "_source": "yahoo_finance",
                        "_cached": False
                    }
    
    except (HTTPError, URLError, json.JSONDecodeError, KeyError, IndexError) as e:
        pass  # Fall through to return None
    
    return None


def fetch_market_data(
    symbol: str,
    endpoint: str,
    api_key: Optional[str] = None,
    use_cache: bool = True,
    use_fallback: bool = True
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Fetch market data with caching and fallback.
    
    Returns:
        Tuple of (data_dict, source_string)
        source_string: "cache", "alphavantage", "yahoo_finance", or "error"
    """
    cache_path = _get_cache_path(symbol, endpoint)
    
    # Check cache first
    if use_cache and _is_cache_valid(cache_path, endpoint):
        cached_data = _read_cache(cache_path)
        if cached_data:
            cached_data["_cached"] = True
            return cached_data, "cache"
    
    # Try Alpha Vantage
    if api_key:
        _wait_for_rate_limit()
        
        # Map endpoint to Alpha Vantage API
        av_endpoints = {
            "quote": "GLOBAL_QUOTE",
            "overview": "OVERVIEW",
            "income": "INCOME_STATEMENT",
            "balance": "BALANCE_SHEET",
            "cashflow": "CASH_FLOW",
            "daily": "TIME_SERIES_DAILY",
            "news": "NEWS_SENTIMENT"
        }
        
        av_endpoint = av_endpoints.get(endpoint, endpoint.upper())
        
        # Build URL
        base_url = "https://www.alphavantage.co/query"
        if endpoint == "news":
            url = f"{base_url}?function={av_endpoint}&tickers={symbol}&apikey={api_key}"
        else:
            url = f"{base_url}?function={av_endpoint}&symbol={symbol}&apikey={api_key}"
        
        try:
            req = Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            with urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Check for API error messages
                if "Error Message" in data or "Information" in data:
                    raise ValueError(f"API Error: {data.get('Error Message', data.get('Information', 'Unknown'))}")
                
                _update_rate_limit()
                
                # Cache the result
                if use_cache:
                    data["_source"] = "alphavantage"
                    data["_cached"] = False
                    _write_cache(cache_path, data)
                
                return data, "alphavantage"
        
        except Exception as e:
            # Log for debugging but continue to fallback
            print(f"Alpha Vantage failed: {e}", file=sys.stderr)
            pass
    
    # Try Yahoo Finance fallback
    if use_fallback:
        yahoo_data = _fetch_yahoo_finance(symbol, endpoint)
        if yahoo_data:
            if use_cache:
                _write_cache(cache_path, yahoo_data)
            return yahoo_data, "yahoo_finance"
    
    return None, "error"


def clear_cache(symbol: Optional[str] = None, endpoint: Optional[str] = None) -> int:
    """
    Clear cached data.
    
    Args:
        symbol: If provided, only clear cache for this symbol
        endpoint: If provided, only clear cache for this endpoint
    
    Returns:
        Number of cache files deleted
    """
    if not CACHE_DIR.exists():
        return 0
    
    deleted = 0
    
    for cache_file in CACHE_DIR.glob("*.json"):
        if symbol and endpoint:
            # Check if this file matches the symbol+endpoint
            expected_key = _get_cache_key(symbol, endpoint)
            if cache_file.stem == expected_key:
                cache_file.unlink()
                deleted += 1
        else:
            # Clear all or filter by criteria
            cache_file.unlink()
            deleted += 1
    
    return deleted


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch market data with caching and rate limiting"
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
    parser.add_argument("--no-fallback", action="store_true", help="Don't use Yahoo Finance fallback")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache for this symbol/endpoint")
    parser.add_argument("--stdin", action="store_true", help="Read parameters from stdin as JSON")
    
    args = parser.parse_args()
    
    # Handle stdin input
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
        
        if not args.symbol or not args.endpoint:
            print("Error: stdin JSON must contain 'symbol' and 'endpoint'", file=sys.stderr)
            sys.exit(1)
        
        if not args.symbol or not args.endpoint:
            print("Error: stdin JSON must contain 'symbol' and 'endpoint'", file=sys.stderr)
            sys.exit(1)
    
    # Clear cache if requested
    if args.clear_cache:
        deleted = clear_cache(args.symbol, args.endpoint)
        print(f"Cleared {deleted} cache file(s)")
        sys.exit(0)
    
    # Get API key from environment
    api_key = os.environ.get("ALPHAVANTAGE_API_KEY")
    
    # Fetch data
    data, source = fetch_market_data(
        symbol=args.symbol,
        endpoint=args.endpoint,
        api_key=api_key,
        use_cache=not args.no_cache,
        use_fallback=not args.no_fallback
    )
    
    if data is None:
        print(f"Error: Failed to fetch data for {args.symbol} ({args.endpoint})", file=sys.stderr)
        sys.exit(1)
    
    # Output
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
