import asyncio
import aiohttp
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import logging
from app.db.mongodb import get_mongodb
from app.services.encoder import encode_text
from app.db.pinecone import connect_to_pinecone
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create a thread pool executor for Pinecone operations
executor = ThreadPoolExecutor(max_workers=5)

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def parse_article(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h1').text.strip()
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
        await asyncio.get_event_loop().run_in_executor(
            executor,
            pinecone_index.upsert,
            [(str(article_id.inserted_id), vector, {"url": url, "title": title})]
        )
        logging.info(f"Successfully scraped and stored article: {url}")
    except Exception as e:
        logging.error(f"Error processing article {url}: {str(e)}")

async def scrape_news():
    news_urls = [
        "https://www.bbc.com/",
        "https://www.reuters.com/",
        # Add more URLs as needed
    ]
    
    pinecone_index = connect_to_pinecone()
    
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_and_store_article(session, url, pinecone_index) for url in news_urls]
        await asyncio.gather(*tasks)

# This function can be called to start the scraping process
def start_scraping():
    asyncio.run(scrape_news())

if __name__ == "__main__":
    start_scraping()