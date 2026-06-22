from fastmcp import FastMCP
import yfinance as yf
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("lme-price")

TICKER_MAP = {
    "copper": "HG=F",
    "zinc": "ZNC=F",
    "nickel": "NIK=F",
    "lithium": "LIT",
    "iron": "TIO=F"
}

@mcp.tool()
def get_price(commodity: str, date: str = None) -> str:
    """
    Get the price of a specific commodity.
    
    Args:
        commodity: Name of the commodity (e.g. 'copper', 'zinc', 'nickel', 'lithium', 'iron')
        date: Optional date in YYYY-MM-DD format. Defaults to today.
    """
    commodity = commodity.lower()
    ticker_symbol = TICKER_MAP.get(commodity, commodity)

    try:
        ticker = yf.Ticker(ticker_symbol)
        if date:
            start_date = datetime.strptime(date, "%Y-%m-%d")
            end_date = start_date + timedelta(days=1)
            hist = ticker.history(start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"))
        else:
            hist = ticker.history(period="1d")
            
        if hist.empty:
            return f"No price data found for {commodity} on {date or 'today'}."
            
        price = hist['Close'].iloc[0]
        date_str = hist.index[0].strftime('%Y-%m-%d')
        return f"{commodity.capitalize()} price on {date_str} was {price:.2f}."
    except Exception as e:
        logger.error(f"Failed to get price: {e}")
        return f"Failed to retrieve price for {commodity}: {str(e)}"

@mcp.tool()
def get_trend(commodity: str, days: int = 30) -> str:
    """
    Get the price trend of a specific commodity over the last N days.
    
    Args:
        commodity: Name of the commodity
        days: Number of days to look back
    """
    commodity = commodity.lower()
    ticker_symbol = TICKER_MAP.get(commodity, commodity)

    try:
        ticker = yf.Ticker(ticker_symbol)
        if days <= 5: period = "5d"
        elif days <= 30: period = "1mo"
        elif days <= 90: period = "3mo"
        else: period = "1y"
            
        hist = ticker.history(period=period)
        if hist.empty or len(hist) < 2:
            return f"Not enough data to calculate trend for {commodity}."
            
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        change = ((end_price - start_price) / start_price) * 100
        
        trend = "Upward" if change > 0 else "Downward"
        return f"{commodity.capitalize()} trend over {days} days is {trend} ({change:+.2f}%). Start: {start_price:.2f}, End: {end_price:.2f}."
    except Exception as e:
        logger.error(f"Failed to get trend: {e}")
        return f"Failed to retrieve trend for {commodity}: {str(e)}"

if __name__ == "__main__":
    mcp.run()
