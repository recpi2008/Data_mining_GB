from pathlib import Path
import time
from datetime import datetime
import requests
from urllib.parse import urljoin
import bs4
import pymongo

month_dict = {'января':'01',
              'февраля':'02',
              'марта':'03',
              'апреля':'04',
              'мая':'05',
              'июня':'06',
              'июля':'07',
              'августа':'08',
              'сентября':'09',
              'октября':'10',
              'ноября':'11',
              'декабря':'12'}

class MagnitParse:
    def __init__(self, start_url, mongo_url):
        self.start_url = start_url
        client = pymongo.MongoClient(mongo_url)
        self.db = client["gb_parse_19_03_21"]

    def get_response(self, url, *args, **kwargs):
        for _ in range(15):
            response = requests.get(url, *args, **kwargs)
            if response.status_code == 200:
                return response
            time.sleep(1)
        raise ValueError("URL DIE")

    def get_soup(self, url, *args, **kwargs) -> bs4.BeautifulSoup:
        soup = bs4.BeautifulSoup(self.get_response(url, *args, **kwargs).text, "lxml")
        return soup

    @property
    def template(self):
        data_template = {
            "url": lambda a: urljoin(self.start_url, a.attrs.get("href", "/")),
            "product_name": lambda a: a.find('div', attrs= {'class':"card-sale__title"}).text,
            "image_url": lambda a: urljoin(
                self.start_url, a.find('picture').find('img').attrs.get('data-src', '/')),
            "name_sale": lambda a: a.find('div', attrs = {'class':'card-sale__header'}).text,
            "badge_name": lambda a: a.find('div', attrs={'class': 'badge__title'}).text,
            "badge_val": lambda a: a.find('div', attrs={'class': 'badge__val'}).text if True else None,
            "badge_small": lambda a: a.find('div', attrs={'class': 'badge__small'}).text if True else None,
            "label_discount": lambda a: a.find('div', attrs = {'class':'label label_sm label_magnit card-sale__discount'}).text if True else None,
            'label__price_old': lambda a: float('.'.join(a.find('div', attrs = {'class':'label__price label__price_old'}).text.split())) if True else None,
            'label__price_new': lambda a: '.'.join(a.find('div', attrs={'class': 'label__price label__price_new'}).text.split()) if True else None,
            'sale_date': lambda a: ' '.join(a.find('div', attrs={'class': 'card-sale__date'}).text.split()) if True else None,
            'from_data': lambda a: datetime.strptime(month_dict[a.find('div', attrs={'class': 'card-sale__date'}).find('p').text.split()[-1]] +'-'+ a.find('div', attrs={'class': 'card-sale__date'}).find('p').text.split()[-2], "%m-%d").strftime("%d.%m."),
            'till_data': lambda a: datetime.strptime(month_dict[a.find('div', attrs={'class': 'card-sale__date'}).text.split()[-1]] +'-'+ a.find('div', attrs={'class': 'card-sale__date'}).text.split()[-2], "%m-%d").strftime("%d.%m.")

        }
        return data_template

    def run(self):
        for product in self._parse(self.get_soup(self.start_url)):
            self.save(product)

    def _parse(self, soup):
        products_a = soup.find_all("a", attrs={"class": "card-sale"})
        for prod_tag in products_a:
            product_data = {}
            for key, func in self.template.items():
                try:
                    product_data[key] = func(prod_tag)
                except AttributeError:
                    pass
            yield product_data

    def save(self, data):
        collection = self.db["magnit"]
        collection.insert_one(data)


if __name__ == "__main__":
    url = "https://magnit.ru/promo/"
    mongo_url = "mongodb://localhost:27017"
    parser = MagnitParse(url, mongo_url)
    parser.run()