# in app/scraper/spider.py

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from app.db.mongodb import get_mongodb
from app.services.encoder import encode_text
from app.db.pinecone import connect_to_pinecone
import logging

logger = logging.getLogger(__name__)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def parse_article(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h1').text.strip() if soup.find('h1') else "No title found"
    content = ' '.join([p.text for p in soup.find_all('p')])
    return title, content

async def scrape_and_store_article(session, url, pinecone_index):
    try:
        html = await fetch(session, url)
        title, content = await parse_article(html)
        
        # Store in MongoDB
        db = await get_mongodb()
        article_id = await db.articles.insert_one({
            "url": url,
            "title": title,
            "content": content
        })
        
        # Encode and store in Pinecone
        vector = encode_text(title + " " + content)
        pinecone_index.upsert([(str(article_id.inserted_id), vector, {"url": url, "title": title})])
        logger.info(f"Successfully scraped and stored article: {url}")
    except Exception as e:
        logger.error(f"Error processing article {url}: {str(e)}")

async def scrape_news():
    news_urls = [
        "https://www.bbc.com/news",
        "https://www.reuters.com/world/",
        # Add more URLs as needed
    ]
    
    pinecone_index = connect_to_pinecone()
    
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_and_store_article(session, url, pinecone_index) for url in news_urls]
        await asyncio.gather(*tasks)

    logger.info("Scraping process completed")