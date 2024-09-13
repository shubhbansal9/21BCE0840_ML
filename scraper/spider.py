import scrapy
from app.db.mongodb import store_document
from app.db.pinecone import store_vector
from app.services.encoder import encode_text

class NewsSpider(scrapy.Spider):
    name = "news_spider"
    start_urls = [
        'https://example-news-site.com/latest',
    ]

    def parse(self, response):
        for article in response.css('article'):
            title = article.css('h2::text').get()
            content = article.css('div.content::text').get()
            url = article.css('a::attr(href)').get()
            
            document = {
                'title': title,
                'content': content,
                'url': url
            }
            
            doc_id = store_document(document)
            
            vector = encode_text(title + " " + content)
            store_vector(str(doc_id), vector, {'url': url})
            
            yield document