from scrapy.crawler import CrawlerProcess # основной управляющий процесс
from scrapy.settings import Settings # основной класс конфигуратор
from gb_parse.spiders.autoyoula import AutoyoulaSpider # импортируем паука

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    crawler_proc.crawl(AutoyoulaSpider)
    crawler_proc.start()

