import threading
import schedule
import time
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from .spider import NewsSpider

def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl(NewsSpider)
    process.start()

def run_scheduler():
    schedule.every(6).hours.do(run_spider)
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_scheduler():
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()