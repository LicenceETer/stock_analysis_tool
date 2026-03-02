"""Financial news fetching tools for A-Share MCP Agent."""

import logging
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, quote

logger = logging.getLogger(__name__)


def get_market_news(
    symbol: str, 
    keywords: Optional[str] = None, 
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """Fetch recent financial news for a stock or keywords.
    
    Args:
        symbol: Stock code (e.g., "600519")
        keywords: Optional additional keywords to search for
        max_results: Maximum number of news items to return (default: 5)
        
    Returns:
        List of news items with title, summary, URL, source, and timestamp
        
    Raises:
        ValueError: If symbol is invalid or news cannot be retrieved
    """
    try:
        # Validate inputs
        if not symbol or not isinstance(symbol, str):
            raise ValueError("Invalid symbol format")
            
        # Build search query
        search_query = symbol
        if keywords:
            search_query += f" {keywords}"
            
        # Try multiple sources
        news_items = []
        
        # Try East Money (东方财富) first
        try:
            east_money_news = _fetch_east_money_news(search_query, max_results)
            news_items.extend(east_money_news)
        except Exception as e:
            logger.warning(f"Failed to fetch from East Money: {str(e)}")
            
        # Try Sina Finance (新浪财经) if needed
        if len(news_items) < max_results:
            try:
                sina_news = _fetch_sina_finance_news(search_query, max_results - len(news_items))
                news_items.extend(sina_news)
            except Exception as e:
                logger.warning(f"Failed to fetch from Sina Finance: {str(e)}")
                
        # Deduplicate and limit results
        seen_titles = set()
        unique_news = []
        for item in news_items:
            if item["title"] not in seen_titles and len(unique_news) < max_results:
                seen_titles.add(item["title"])
                unique_news.append(item)
                
        logger.info(f"Successfully fetched {len(unique_news)} news items for {symbol}")
        return unique_news[:max_results]
        
    except Exception as e:
        logger.error(f"Error in get_market_news for {symbol}: {str(e)}")
        raise ValueError(f"Failed to fetch market news: {str(e)}")


def _fetch_east_money_news(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Fetch news from East Money (东方财富网).
    
    Args:
        query: Search query
        max_results: Maximum number of results to fetch
        
    Returns:
        List of news items
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # East Money search URL
    search_url = f"https://search.eastmoney.com/bulletin/s?cb=jQuery&keyword={quote(query)}&page=1&sort=1"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the JSONP response
        content = response.text
        if "jQuery(" in content:
            json_str = content.split("jQuery(", 1)[1].rsplit(")", 1)[0]
            import json
            data = json.loads(json_str)
            
            news_items = []
            for item in data.get("data", []):
                if len(news_items) >= max_results:
                    break
                    
                news_items.append({
                    "title": item.get("title", ""),
                    "summary": item.get("digest", ""),
                    "url": item.get("url", ""),
                    "source": "East Money",
                    "publish_time": item.get("date", ""),
                    "sentiment": "neutral"  # Sentiment analysis would require additional processing
                })
                
            return news_items
            
    except Exception as e:
        logger.error(f"Error fetching from East Money: {str(e)}")
        raise


def _fetch_sina_finance_news(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Fetch news from Sina Finance (新浪财经).
    
    Args:
        query: Search query
        max_results: Maximum number of results to fetch
        
    Returns:
        List of news items
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Sina Finance search URL
    search_url = f"https://search.sina.com.cn/?c=news&q={quote(query)}&range=title&time=day&num=20"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = []
        
        # Find news items in the search results
        for item in soup.find_all('div', class_='box-result'):
            if len(news_items) >= max_results:
                break
                
            title_elem = item.find('h2')
            if not title_elem:
                continue
                
            link_elem = title_elem.find('a')
            if not link_elem:
                continue
                
            title = link_elem.get_text().strip()
            url = link_elem.get('href', '')
            
            # Get summary
            summary_elem = item.find('p', class_='content')
            summary = summary_elem.get_text().strip() if summary_elem else ""
            
            # Get source and time
            info_elem = item.find('span', class_='fgray_time')
            info_text = info_elem.get_text().strip() if info_elem else ""
            
            news_items.append({
                "title": title,
                "summary": summary,
                "url": url,
                "source": "Sina Finance",
                "publish_time": info_text,
                "sentiment": "neutral"
            })
            
        return news_items
        
    except Exception as e:
        logger.error(f"Error fetching from Sina Finance: {str(e)}")
        raise