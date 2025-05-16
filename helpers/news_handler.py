import aiohttp
import feedparser
import asyncio
from datetime import datetime
from helpers.response_manager import Response_Manager  
import random
from bs4 import BeautifulSoup


class NewsHandler():
    def __init__(self, picrawler_instance):
        self.picrawler_instance = picrawler_instance
        self.response_manager = Response_Manager(picrawler_instance)

        # RSS Feeds categorized (1 source per category)
        self.rss_feeds = {
            "nature": "https://www.natureconservancy.ca/system/rss/channel.jsp?feedID=464872245",
            "tech": "https://www.cbc.ca/webfeed/rss/rss-technology",
        }

    async def fetch_news(self, category):
        """Fetches a random news headline from a category's RSS feed."""
        feed_url = self.rss_feeds.get(category)
        if not feed_url:
            return None  # No feed available for this category
        
        articles = await self.fetch_news_feed(feed_url)

        if not articles:
            return None  # No articles found

        # Choose a random article from the list
        selected_article = random.choice(articles)
        return selected_article

    async def fetch_news_feed(self, url, timeout=5):
        """Fetches and parses an RSS feed with a timeout and User-Agent."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }
        client_timeout = aiohttp.ClientTimeout(total=timeout)
        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=client_timeout) as response:
                    if response.status == 200:
                        data = await response.text()
                        feed = feedparser.parse(data)
                        articles = []
                        for entry in feed.entries:
                            # Prefer 'summary' if available, otherwise 'description'
                            summary = self.extract_text(getattr(entry, 'summary', getattr(entry, 'description', '')))
                            title = self.extract_text(entry.title)
                            articles.append({"title": title, "description": summary})
                        return articles
                    else:
                        print(f"Failed to fetch RSS feed: {url} (Status Code: {response.status})")
                        return []
        except asyncio.TimeoutError:
            print(f"Timeout: RSS feed {url} took too long to respond.")
        except aiohttp.ClientError as e:
            print(f"Network error while fetching RSS feed {url}: {str(e)}")
        
        return []

    async def startup_fetch_news(self, llm_client):
        """Fetches and returns one random headline from the available news categories."""
        articles = []
        for category in self.rss_feeds.keys():
            article = await self.fetch_news(category)
            if article:
                articles.append(article)  # article is a dict with 'title' and 'description'
            else:
                print(f"No article added for category {category}")
        
        if articles:
            # Choose one random article from the list
            selected_article = random.choice(articles)
            # Add only the chosen article's title to conversation history
            llm_client.conversation_history.append({
                "role": "system", 
                "content": selected_article["title"]
            })
            await self.response_manager.speak_with_flite("News connection established. Headlines have been preeloaded.")
            return selected_article["title"]
        else:
            await self.response_manager.speak_with_flite("Unable to retrieve news at this time.")
            return None

    
    @staticmethod
    def current_datetime():
        """Returns the current date and time as a formatted string."""
        return datetime.now().strftime("%A, %B %d, %Y. The time is %I:%M %p.")

    @staticmethod
    def extract_text(content):
        """Extract plain text from a string that might contain HTML."""
        if content:
            return BeautifulSoup(content, "html.parser").get_text(separator=" ", strip=True)
        return ""