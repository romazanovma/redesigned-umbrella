import functools
import json

import scrapy


CATEGORY_MENU = "https://www.wildberries.ru/webapi/menu/main-menu-ru-ru.json"
SUBCATEGORY_URL = "https://catalog.wb.ru/catalog/men_clothes/catalog?curr=rub&lang=ru&locale=ru&"
PRODUCTS_URL = "https://card.wb.ru/cards/detail?locale=ru&lang=ru&curr=rub&dest=-1075831&nm="


class MySpider(scrapy.Spider):
    name = 'wb'
    allowed_domains = ['wildberries.ru/']

    def __init__(self, category, subcategory, page=1, name=None, **kwargs):
        if category and subcategory:
            self.category = category
            self.subcategory = subcategory
            self.page = page
            super().__init__(name, **kwargs)
        else:
            self.log(f"usage: scrapy crawl -a category=CATEGORY -a subcategory=SUBCATEGORY -a page=PAGE(optional) wb")
            exit()

    def start_requests(self):
        url = CATEGORY_MENU
        yield scrapy.Request(url, callback=self.get_query)

    def get_query(self, response):
        category_object = [category for category in json.loads(response.body) if category["name"]==self.category][0]
        subcategory_object = [subcategory for subcategory in category_object["childs"] if subcategory["name"]==self.subcategory][0]
        subcategory_query = subcategory_object["query"]
        self.log(f'Got query for subcategory: {subcategory_query}')
        url = f"{SUBCATEGORY_URL}{subcategory_query}&page={self.page}"
        # for category in json.loads(response.body):
        #     if category["name"] == category_name:
        #         for subcategory in category["childs"]:
        #             if subcategory["name"] == subcategory_name:
        #                 subcategory_query = subcategory["query"]
        #                 self.log(f'Got query for subcategory: {subcategory_query}')
        #                 break
        #         break
        yield scrapy.Request(url, callback=self.parse_category,dont_filter=True)

    def parse_category(self, response):
        products_list = json.loads(response.body)["data"]["products"]
        url = PRODUCTS_URL
        for product in products_list:
            url += f'{product["id"]};'
        yield scrapy.Request(url, callback=self.parse_card,dont_filter=True)

    def parse_card(self, response):
        cards_list = json.loads(response.body)["data"]["products"]
        with open("cards_snapshot.result", 'w') as f:
            for card in cards_list:
                parsed_card = {
                    "id": card["id"],
                    "name": card["name"],
                    "brand": card["brand"],
                    "price": card["salePriceU"],
                    "old_price": card["priceU"],
                    "rating": card["rating"],
                    "feedbacks": card["feedbacks"],
                    "sizes": [
                        {"name": size["name"], "count": functools.reduce(lambda x,y: x+y['qty'],size["stocks"],0)} for size in card["sizes"]
                        ],
                    # "count": size["stocks"]
                }
                f.write(f'{parsed_card}\n')
