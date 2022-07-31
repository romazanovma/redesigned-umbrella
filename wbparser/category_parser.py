import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from db import *


def list_get(list, idx, default):
    '''safe get method for list'''
    try:
        return list[idx]
    except IndexError:
        return default


DELAY = 3


# python3 category_parser.py "https://www.wildberries.ru/" "Мужчинам" "Верхняя одежда" 5
def main(*args):
    if len(args) >= 4:
        driver = webdriver.Firefox()
        db = Db()
        db.drop()
        link = link_build(driver, website=list_get(args,1,None),
            category=list_get(args,2,None), subcategory=list_get(args,3,None),
            page=list_get(args,4,1))
        if link == None:
            print("Category not found")
        else:
            print(link)
            parsed = parse(driver, link)
            db.write_db(parsed)
        show = db.get()
        for item in show:
                print(f'{item.id}\t{item.brand}\t{item.card_name}\t{item.name}\t{item.price}\t{item.old_price}\t{item.description}\t{item.rating}\n')
        driver.close()
    else:
        print("usage: python3 category_parser.py website category subcategory page(optional)")

def link_build(driver, website, category=None, subcategory=None, page=1, delay=DELAY):
    try:
        driver.get(website)
        try:
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.menu-burger__main-list-item")))
        except TimeoutException:
            print("Error: get website page Timeout")
        menu = driver.find_elements(By.CSS_SELECTOR, "li.menu-burger__main-list-item")
        link = None
        if category:
            for elem in menu:
                link_elem = elem.find_element(By.CSS_SELECTOR, "a.menu-burger__main-list-link")
                if link_elem.get_attribute("text")==category:
                    link = link_elem.get_attribute("href")
            if subcategory:
                driver.get(link)
                try:
                    WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.j-menu-item")))
                except TimeoutException:
                    print("Error: get category page Timeout")
                menu = driver.find_elements(By.CSS_SELECTOR, "a.j-menu-item")
                for elem in menu:
                    if elem.get_attribute("text")==subcategory:
                        link = elem.get_attribute("href")
            link+=f"?page={page}"
        return link

    except Exception as e:
        print(f"Exception in link_build:\n{e}")

def parse(driver, link):
    driver.get(link)
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.product-card__main")))
    except TimeoutException:
        print("Error: get subcategory page Timeout")
    catalog = driver.find_elements(By.CSS_SELECTOR, "a.product-card__main")
    card_list = []
    for product in catalog:
        product_link = product.get_attribute("href")
        brand = product.find_element(By.CSS_SELECTOR, "strong.brand-name").text
        card_name = product.find_element(By.CSS_SELECTOR, "span.goods-name").text
        price = product.find_element(By.CLASS_NAME, "lower-price").text
        try:
            old_price = product.find_element(By.CLASS_NAME, "price-old-block").text
        except Exception:
            old_price = None
        driver.get(product_link)
        try:
            WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.product-article")))
        except TimeoutException:
            print("Error: get product page Timeout")
        id = driver.find_element(By.CSS_SELECTOR, "p.product-article").text.replace("Арт: ", "").replace("Артикул: ", "")
        name = driver.find_element(By.CSS_SELECTOR, "h1").text
        description = driver.find_element(By.CSS_SELECTOR, "p.collapsable__text").text
        try:
            rating = driver.find_element(By.CSS_SELECTOR, "span.address-rate-mini").text
        except Exception:
            rating = None
        card = {
            "id": id,
            "brand": brand,
            "card_name": card_name,
            "name": name,
            "price": price,
            "old_price": old_price,
            "description": description,
            "rating": rating
        }
        card_list.append(card)
        driver.back()
        try:
            WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.pagination-item")))
        except TimeoutException:
            print("Error: driver.back() Timeout")
    return card_list


if __name__ == "__main__":
    main(*sys.argv)
