import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page
import json
import asyncio
import mcp

from typing import List, Dict, Optional

class NewsScraper:
    """
    A class to scrape news articles from specified websites.
    """

    def __init__(self, urls: List[str]):
        self.urls = urls

    def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from a URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            Optional[str]: HTML content if successful, None otherwise.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_articles(self, html: str, parser: str = 'html.parser') -> List[Dict]:
        """
        Parse HTML to extract article information.

        Args:
            html (str): HTML content.
            parser (str): Parser type for BeautifulSoup.

        Returns:
            List[Dict]: List of articles with title and link.
        """
        articles = []
        try:
            soup = BeautifulSoup(html, parser)
            for item in soup.find_all('article'):
                title_tag = item.find('h2') or item.find('h3')
                link_tag = item.find('a', href=True)
                if title_tag and link_tag:
                    articles.append({
                        'title': title_tag.get_text(strip=True),
                        'link': link_tag['href']
                    })
        except Exception as e:
            print(f"Error parsing HTML: {e}")
        return articles

    def scrape(self) -> List[Dict]:
        """
        Scrape all URLs and extract articles.

        Returns:
            List[Dict]: Aggregated list of articles from all URLs.
        """
        all_articles = []
        for url in self.urls:
            html = self.fetch_html(url)
            if html:
                articles = self.parse_articles(html)
                all_articles.extend(articles)
        return all_articles

class BrowserAutomation:
    """
    A class to automate browser interactions using Playwright.
    """

    def __init__(self):
        self.browser: Optional[Browser] = None

    async def launch(self):
        """
        Launch the Playwright browser.
        """
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
        except Exception as e:
            print(f"Error launching browser: {e}")

    async def close(self):
        """
        Close the Playwright browser.
        """
        if self.browser:
            await self.browser.close()

    async def navigate_and_interact(self, url: str, actions: Optional[List[Dict]] = None) -> Optional[str]:
        """
        Navigate to a URL and perform actions.

        Args:
            url (str): URL to navigate.
            actions (Optional[List[Dict]]): List of actions to perform.

        Returns:
            Optional[str]: Page content after interactions.
        """
        if not self.browser:
            print("Browser not initialized.")
            return None
        try:
            page: Page = await self.browser.new_page()
            await page.goto(url)
            if actions:
                for action in actions:
                    if action['type'] == 'click':
                        await page.click(action['selector'])
                    elif action['type'] == 'fill':
                        await page.fill(action['selector'], action['value'])
                    # Add more actions as needed
            content = await page.content()
            await page.close()
            return content
        except Exception as e:
            print(f"Error during navigation/interactions: {e}")
            return None

class NewsFilter:
    """
    A class to filter news articles based on keywords or other criteria.
    """

    def __init__(self, keywords: List[str]):
        self.keywords = [kw.lower() for kw in keywords]

    def filter_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Filter articles containing specified keywords.

        Args:
            articles (List[Dict]): List of articles.

        Returns:
            List[Dict]: Filtered list of articles.
        """
        filtered = []
        for article in articles:
            title_lower = article['title'].lower()
            if any(keyword in title_lower for keyword in self.keywords):
                filtered.append(article)
        return filtered

class NewsletterGenerator:
    """
    A class to generate a summarized daily newsletter.
    """

    def __init__(self, articles: List[Dict]):
        self.articles = articles

    def generate_summary(self) -> str:
        """
        Generate a simple text summary of articles.

        Returns:
            str: The newsletter content.
        """
        if not self.articles:
            return "No news articles available today."
        summary_lines = ["Daily News Summary:\n"]
        for idx, article in enumerate(self.articles, 1):
            summary_lines.append(f"{idx}. {article['title']}\nLink: {article['link']}\n")
        return "\n".join(summary_lines)

# Example usage functions (to be called from main.py or other orchestrator)
async def run_full_pipeline():
    """
    Run the entire news scraping, filtering, browser automation, and newsletter generation.
    """
    # Initialize scraper with example URLs
    scraper = NewsScraper([
        'https://example-news-site.com',
        # Add more news URLs as needed
    ])

    # Scrape articles
    articles = scraper.scrape()

    # Filter articles
    filter_keywords = ['technology', 'science', 'innovation']
    news_filter = NewsFilter(filter_keywords)
    filtered_articles = news_filter.filter_articles(articles)

    # Generate newsletter
    newsletter = NewsletterGenerator(filtered_articles)
    summary = newsletter.generate_summary()

    # Automate browser interactions if needed
    browser_auto = BrowserAutomation()
    await browser_auto.launch()
    # Example interaction
    content = await browser_auto.navigate_and_interact('https://some-interaction-site.com', actions=[
        {'type': 'click', 'selector': '#start-button'},
        {'type': 'fill', 'selector': '#search-box', 'value': 'latest news'}
    ])
    await browser_auto.close()

    # Return or send the newsletter content
    return summary