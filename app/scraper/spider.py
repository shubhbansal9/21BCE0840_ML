import asyncio
import aiohttp
from bs4 import BeautifulSoup
from app.db.mongodb import get_mongodb
from app.services.encoder import encode_text
from app.db.pinecone import connect_to_pinecone
import logging

logger = logging.getLogger(__name__)

async def fetch(session, url):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                logger.warning(f"Failed to fetch {url}: HTTP {response.status}")
                return None
            return await response.text()
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error for {url}: {str(e)}")
        return None
    except asyncio.TimeoutError:
        logger.error(f"Timeout error for {url}")
        return None


async def parse_article(html):
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h1')
    if title:
        title = title.text.strip()
    else:
        title = soup.title.text.strip() if soup.title else "No title found"
    
    content = ' '.join([p.text for p in soup.find_all('p') if len(p.text.split()) > 20])
    return title, content


async def scrape_and_store_article(session, url, pinecone_index):
    try:
        html = await fetch(session, url)
        if not html:
            return

        title, content = await parse_article(html)
        
        if not content or len(content.split()) < 50:
            logger.warning(f"Insufficient content for {url}")
            return
        db = await get_mongodb()
        # existing_article = await db.articles.find_one({"url": url})
        # if existing_article:
        #     logger.info(f"Article already exists in MongoDB for URL: {url}")
        #     return

        article_id = await db.articles.insert_one({
            "url": url,
            "title": title,
            "content": content
        })
        vector = encode_text(title + " " + content)
        pinecone_index.upsert([(str(article_id.inserted_id), vector, {"url": url, "title": title})])
        logger.info(f"Successfully upserted to Pinecone: {url}")
        
    except Exception as e:
        logger.error(f"Error processing article {url}: {str(e)}")


async def scrape_news():
    news_urls = [
        "https://www.bbc.com/news",
        "https://news.mit.edu/topic/machine-learning",
        "https://www.nature.com/natmachintell/",
        "https://techcrunch.com/",
        "https://www.newyorker.com/tag/black-lives-matter",
        "https://www.nasa.gov/missions/artemis/artemis-iii/",
        "https://www.economist.com/climate-change",
    ]
    
    pinecone_index = connect_to_pinecone()
    
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_and_store_article(session, url, pinecone_index) for url in news_urls]
        await asyncio.gather(*tasks)

    logger.info("Scraping process completed")