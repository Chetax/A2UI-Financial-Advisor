# backend/app/tools.py
"""
Tool-calling layer (ReAct pattern): fetches real stock data via yfinance.
Per SESSION_1.md decision: "wrapped with a fallback so a flaky source
can't sink the demo." This module is TOTAL — get_stock_data() never
raises. On any failure it returns a dict with an "error" key instead,
so callers can detect failure and fall back to LLM-only behavior
without crashing the chat turn.
"""
import yfinance as yf
import re


_TICKER_PATTERN = re.compile(r"\b[A-Z]{2,10}\b")


# marketCap comes back in raw rupees (e.g. 17565149560832). Converting to
# "L Cr" (lakh crore) here, once, so both the prompt and the card show
# the same human-readable unit your original hardcoded sample used.
def _format_market_cap(raw: float | None) -> str | None:
    if raw is None:
        return None
    cr = raw / 1e7          # 1 crore = 1e7
    l_cr = cr / 1e5         # 1 lakh crore = 1e5 crore
    return f"₹{l_cr:.1f}L Cr"



def extract_tickers(text: str) -> list[str]:
    """
    Heuristic ticker detection: any ALL-CAPS word, 2-10 letters.
    Good enough for 'Compare RELIANCE and TCS' style messages.
    Not perfect (would also match 'USD' or 'CEO'), acceptable tradeoff
    for a demo — a real product would validate against a ticker list.
    """
    return list(dict.fromkeys(_TICKER_PATTERN.findall(text)))  # dedupe, keep order


def get_stock_data(symbol: str) -> dict:
    """
    symbol: NSE ticker WITHOUT suffix, e.g. 'RELIANCE', 'TCS'.
    This function appends '.NS' itself, so callers pass plain names.
    Returns a small, prompt-ready dict — never the raw yfinance object.
    On failure, returns {"symbol": symbol, "error": "..."} instead of
    raising, so the caller can check `"error" in result`.
    """
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info

        market_cap_raw = info.get("marketCap")
        pe = info.get("trailingPE")
        sector = info.get("sector")

        if market_cap_raw is None and pe is None and sector is None:
            # yfinance didn't throw, but returned nothing usable —
            # treat as a soft failure too (bad ticker, rate-limited, etc).
            return {"symbol": symbol, "error": "no data returned"}

        return {
            "symbol": symbol,
            "market_cap": _format_market_cap(market_cap_raw),
            "pe_ratio": round(pe, 1) if pe is not None else None,
            "sector": sector,
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def get_multiple(symbols: list[str]) -> list[dict]:
    """Convenience wrapper for the comparison-card flow (2+ tickers)."""
    return [get_stock_data(s) for s in symbols]