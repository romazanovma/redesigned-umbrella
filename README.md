# redesigned-umbrella
Wildberries category parser

usage: category_parser.py [-h] [--category CATEGORY] [--subcategory SUBCATEGORY]

Parse a wildberries subcategory.

optional arguments:
  -h, --help            show this help message and exit
  --category CATEGORY   Specify the category
  --subcategory SUBCATEGORY
                        Specify the subcategory

usage example: python3 category_parser.py --category "Мужчинам" --subcategory "Верхняя одежда"

# scrapy
usage: scrapy crawl -a category=CATEGORY -a subcategory=SUBCATEGORY -a page=PAGE(optional) wb

usage example: scrapy crawl -a category="Мужчинам" -a subcategory="Джинсы" -a page=1 wb

