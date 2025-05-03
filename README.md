# README.md

# Multi-Functional News Aggregator and Newsletter Generator

This project implements a multi-functional agent that scrapes news websites, filters articles, automates browser interactions via MCP Playwright server, and generates a summarized daily newsletter. The system is modular, leveraging custom Python tools and libraries to ensure robustness and flexibility.

## Features

- Scrapes news articles from multiple sources
- Filters articles based on user-defined criteria
- Automates browser interactions using MCP Playwright server
- Summarizes news articles
- Generates a comprehensive daily newsletter

## Files

- `main.py`: Entry point to orchestrate the workflow
- `tools.py`: Contains utility functions for scraping, filtering, browser automation, and summarization
- `requirements.txt`: Lists required dependencies
- `README.md`: This documentation

## Requirements

Ensure you have Python 3.8+ installed. Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Run the main script:

```bash
python main.py
```

## Dependencies

- llama_index
- requests
- beautifulsoup4
- playwright
- mcp
- json
- asyncio

## Notes

- Make sure to install Playwright browsers:

```bash
python -m playwright install
```

- Configure your MCP Playwright server URL and other settings in `main.py` as needed.

---

# Example implementation of core modules

## main.py

```python
import asyncio
from tools import scrape_news, filter_articles, automate_browser, summarize_articles, generate_newsletter

async def main() -> None:
    try:
        # Step 1: Scrape news articles
        articles = await scrape_news()
        # Step 2: Filter articles
        filtered_articles = filter_articles(articles)
        # Step 3: Automate browser interactions if needed
        await automate_browser(filtered_articles)
        # Step 4: Summarize articles
        summaries = await summarize_articles(filtered_articles)
        # Step 5: Generate and send newsletter
        newsletter = generate_newsletter(summaries)
        print("Daily newsletter generated successfully.")
        # Optionally, save or send the newsletter
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

## tools.py

```python
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import asyncio
from playwright.async_api import async_playwright
import json

NEWS_SOURCES = [
    "https://example-news-site.com",
    # Add more news sources here
]

async def scrape_news() -> List[Dict[str, Any]]:
    """
    Scrapes news articles from predefined sources.
    Returns a list of articles with title, link, and summary.
    """
    articles = []
    for source in NEWS_SOURCES:
        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # Example parsing logic; adjust selectors as needed
            for item in soup.select('article'):
                title_tag = item.find('h2')
                link_tag = item.find('a', href=True)
                summary_tag = item.find('p')
                if title_tag and link_tag:
                    articles.append({
                        'title': title_tag.get_text(),
                        'link': link_tag['href'],
                        'summary': summary_tag.get_text() if summary_tag else ''
                    })
        except requests.RequestException as e:
            print(f"Error fetching {source}: {e}")
    return articles

def filter_articles(articles: List[Dict[str, Any]], keywords: List[str] = None) -> List[Dict[str, Any]]:
    """
    Filters articles based on keywords.
    """
    if keywords is None:
        keywords = ['breaking', 'update', 'news']
    filtered = []
    for article in articles:
        if any(keyword.lower() in article['title'].lower() for keyword in keywords):
            filtered.append(article)
    return filtered

async def automate_browser(articles: List[Dict[str, Any]], mcp_server_url: str = "http://localhost:8080") -> None:
    """
    Automates browser interactions via MCP Playwright server.
    For example, opens each article link to fetch additional data.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(mcp_server_url)
            context = await browser.new_context()
            for article in articles:
                page = await context.new_page()
                try:
                    await page.goto(article['link'])
                    # Perform actions as needed, e.g., extract additional info
                except Exception as e:
                    print(f"Error automating {article['link']}: {e}")
                finally:
                    await page.close()
            await browser.close()
    except Exception as e:
        print(f"Browser automation failed: {e}")

async def summarize_articles(articles: List[Dict[str, Any]]) -> List[str]:
    """
    Generates summaries for each article.
    Placeholder implementation; replace with actual summarization logic.
    """
    summaries = []
    for article in articles:
        # Placeholder: use article summary or fetch content for summarization
        summaries.append(f"{article['title']}: {article['summary']}")
    return summaries

def generate_newsletter(summaries: List[str]) -> str:
    """
    Creates a formatted newsletter from summaries.
    """
    newsletter = "Daily News Summary\n\n"
    for summary in summaries:
        newsletter += f"- {summary}\n"
    return newsletter
```

## requirements.txt

```
llama_index
requests
beautifulsoup4
playwright
mcp
json
asyncio
```

---

**Note:** Customize the scraping selectors, MCP server URL, and newsletter formatting as needed for your specific sources and requirements.