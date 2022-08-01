import sys

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

import argparse


DELAY = 3 #timeout in seconds
WEBSITE = "https://www.wildberries.ru/"
CATEGORY_MENU = "ul.menu-burger__main-list"
CATEGORY_LINK = "a.menu-burger__main-list-link"
SUBCATEGORY_MENU = "a.j-menu-item"
PRODUCT_CARD = "a.product-card__main"
PRODUCT_ARTICLE = "p.product-article"


def main(*args):
    try:
        driver = None
        arg_parser = argparse.ArgumentParser(description='Parse a wildberries subcategory.')
        arg_parser.add_argument('--category', help='Specify the category')
        arg_parser.add_argument('--subcategory',help='Specify the subcategory')
        args = vars(arg_parser.parse_args())
        category = args['category']
        subcategory = args['subcategory']
        if category and subcategory:
            driver = init()
            subcategory_link = subcategory_parser(driver, category=category,
            subcategory=subcategory)
            if subcategory_link:
                cards = parse_products(driver, subcategory_link)
                [show_card(card) for card in cards]
                print(f"number of products parsed:{len(cards)}")
            else:
                print("Category not found")
        else:
            arg_parser.print_help()
    finally:
        if driver:
            driver.close()


def show_card(card):
    print('{')
    for key,value in card.items():
        print(f'{key}:"{value}",\n')
    print('}\n')


def init():
    return webdriver.Firefox()


def subcategory_parser(driver, category, subcategory):
    driver.get(WEBSITE)
    WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR, CATEGORY_MENU)))#May add retries
    # category_menu = driver.find_element(By.CSS_SELECTOR, CATEGORY_MENU)
    # category_url = category_menu.find_element(By.CSS_SELECTOR, f"{CATEGORY_LINK}[text='{category}']")
    category_menu = driver.find_elements(By.CSS_SELECTOR, CATEGORY_LINK)
    for category_element in category_menu:
        if category_element.get_attribute("text")==category:
            category_link = category_element.get_attribute("href")
            break #breaks after finds needed category

    driver.get(category_link)
    WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR, SUBCATEGORY_MENU)))
    subcategory_menu = driver.find_elements(By.CSS_SELECTOR, SUBCATEGORY_MENU)#attribute selector instead of cycle
    for subcategory_element in subcategory_menu:
        if subcategory_element.get_attribute("text")==subcategory:
            subcategory_link = subcategory_element.get_attribute("href")
            break #breaks after finds needed subcategory
    return subcategory_link


def parse_products(driver, subcategory_link):
    driver.get(subcategory_link)
    WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_CARD)))
    product_list = driver.find_elements(By.CSS_SELECTOR, PRODUCT_CARD)
    card_list = [parse_product_card(product) for product in product_list]
    return [parse_product_page(driver, card) for card in card_list]


def parse_product_page(driver, card):
    driver.get(card["url"])
    try:
        WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.CSS_SELECTOR, PRODUCT_ARTICLE)))
    except TimeoutException:
        print("Error: Product page Timeout")
    id = find_element_text_safe(driver, By.CSS_SELECTOR, PRODUCT_ARTICLE)
    if id:
        id = id.replace("Арт: ", "").replace("Артикул: ", "")
    name = find_element_text_safe(driver, By.CSS_SELECTOR, "h1")
    description = find_element_text_safe(driver, By.CSS_SELECTOR, "p.collapsable__text")
    rating = find_element_text_safe(driver, By.CSS_SELECTOR, "span.address-rate-mini")
    return {
        "id": id,
        "brand": card["brand"],
        "card_name": card["card_name"],
        "name": name,
        "price": card["price"],
        "old_price": card["old_price"],
        "description": description,
        "rating": rating,
        "url": card["url"],
    }


def parse_product_card(product):
    product_url = product.get_attribute("href")
    brand = find_element_text_safe(product, By.CSS_SELECTOR, "strong.brand-name")
    card_name = find_element_text_safe(product, By.CSS_SELECTOR, "span.goods-name")
    price = find_element_text_safe(product, By.CLASS_NAME, "lower-price")
    old_price = find_element_text_safe(product, By.CLASS_NAME, "price-old-block")
    return {
        "brand": brand,
        "card_name": card_name,
        "price": price,
        "old_price": old_price,
        "url": product_url,
    }


def find_element_text_safe(source, selector, key):
    try:
        element = source.find_element(selector, key).text
    except NoSuchElementException:
        element = None
    return element


def find_element_safe(source, selector, key):
    try:
        element = source.find_element(selector, key)
    except NoSuchElementException:
        element = None
    return element


if __name__ == "__main__":
    main(*sys.argv)
