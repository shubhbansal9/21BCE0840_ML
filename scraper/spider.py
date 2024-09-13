import asyncio
import aiohttp
from bs4 import BeautifulSoup
from app.db.mongodb import get_mongodb
from app.services.encoder import encode_text
import pinecone
from app.core.config import settings

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def parse_article(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h1').text.strip()
    content = ' '.join([p.text for p in soup.find_all('p')])
    return title, content

async def scrape_and_store_article(session, url):
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
    index = pinecone.Index(settings.PINECONE_INDEX_NAME)
    index.upsert([(str(article_id.inserted_id), vector, {"url": url, "title": title})])

async def scrape_news():
    news_urls = [
        "https://www.bbc.com/",
        "https://www.reuters.com/",
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_and_store_article(session, url) for url in news_urls]
        await asyncio.gather(*tasks)
