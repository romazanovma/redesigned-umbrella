import sys

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

def list_get(list, idx, default):
    '''safe get method for list'''
    try:
        return list[idx]
    except IndexError:
        return default


# python3 category_parser.py "https://www.wildberries.ru/" "Мужчинам" "Верхняя одежда" 5
def main(*args):
    driver = webdriver.Firefox()
    link = link_build(driver, website=list_get(args,1,None),
        category=list_get(args,2,None), subcategory=list_get(args,3,None),
        page=list_get(args,4,1))
    if link == None:
        print("Category not found")
    else:
        print(link)
        parsed = parse(driver, link)
    driver.close()

def link_build(driver, website, category=None, subcategory=None, page=1, delay=3):
    try:
        driver.get(website)
        try:
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.menu-burger__main-list-item")))
        except TimeoutException:
            print("Loading took too much time!")
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
                    print("Loading took too much time!")
                menu = driver.find_elements(By.CSS_SELECTOR, "a.j-menu-item")
                for elem in menu:
                    if elem.get_attribute("text")==subcategory:
                        link = elem.get_attribute("href")
            link+=f"?page={page}"
        return link

    except Exception as e:
        print(f"Exception in link_build:\n{e}")

def parse(driver, link, pages_count=1):
    driver.get(link)
    card_list = driver.find_elements(By.CSS_SELECTOR, "a.product-card__main")
    for card in card_list:
        link = card.get_attribute("href")
        brand = card.find_element(By.CSS_SELECTOR, "strong.brand-name")
        card_name = card.find_element(By.CSS_SELECTOR, "span.goods-name")
        price = card.find_element(By.CSS_SELECTOR, "span.price")
        

if __name__ == "__main__":
    main(*sys.argv)