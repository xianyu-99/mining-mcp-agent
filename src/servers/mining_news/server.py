from fastmcp import FastMCP
from duckduckgo_search import DDGS
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("mining-news")

@mcp.tool()
def search(query: str, days: int = 7) -> str:
    """
    Search mining news using DuckDuckGo.
    
    Args:
        query: The search query (e.g. "Pilbara lithium mining")
        days: How many days back to search
    """
    logger.info(f"Searching news for {query} within {days} days")
    results = []
    try:
        timelimit = "d" if days <= 1 else "w" if days <= 7 else "m"
        with DDGS() as ddgs:
            for r in ddgs.text(query + " mining news", max_results=10, timelimit=timelimit):
                results.append(f"Title: {r.get('title')}\nURL: {r.get('href')}\nSummary: {r.get('body')}\n")
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return f"Search failed: {str(e)}"
    
    if not results:
        return "No news found."
    return "\n---\n".join(results)

@mcp.tool()
def fetch_article(url: str) -> str:
    """
    Fetch the full text of an article given its URL.
    
    Args:
        url: The URL of the article
    """
    logger.info(f"Fetching article: {url}")
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return text[:5000] 
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return f"Failed to fetch article: {str(e)}"

if __name__ == "__main__":
    mcp.run()
