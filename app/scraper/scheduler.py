import asyncio
from scraper.spider import scrape_news

async def run_scraper():
    while True:
        await scrape_news()
        await asyncio.sleep(3600)  

def start_scraper():
    loop = asyncio.get_event_loop()
    loop.create_task(run_scraper())