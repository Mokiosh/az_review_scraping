"""This is a scraping program for each ASIN review"""

import datetime
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

now = datetime.datetime.today()
today = now.strftime("%Y%m%d")
month = f"{now:%b}"

options = Options()
options.add_argument('--incognito')
# options.add_argument('--headless')
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()))

input_dir_path = '../input_dir'
output_dir_path = '../output_dir'
asin_file = 'review_ASIN.csv'
columns = ["ASIN", "product", "brand", "name", "date", "score", "title",
           "comment"]

ASIN = []
product = []
brand = []
name = []
date = []
score = []
title = []
comment = []


def scroll_down():
    """Get height of the page, and scroll down by loop"""
    height = driver.execute_script("return document.body.scrollHeight")
    half_height = height // 2
    for x in range(1, half_height):
        driver.execute_script("window.scrollTo(0, " + str(x) + ");")


def find_next_page():
    try:
        driver.find_element(By.XPATH, "//*[@class='a-disabled a-last']")
        # no_next_page.click()
        print("no next page")
        return False
    except:
        try:
            next_page = driver.find_element(By.XPATH, "//*[@class='a-last']")
            next_page.click()
            driver.implicitly_wait(10)
            return True
        except:
            return False


def scraping_review(asin):
    asin_name = driver.find_element(By.CLASS_NAME, "a-list-item").text.replace \
        ("...", "").replace("/", "")
    try:
        brand_name = driver.find_element(By.ID, "cr-arp-byline").text
    except:
        brand_name = ""

    while True:
        driver.implicitly_wait(10)
        scroll_down()

        loop = len([i for i in driver.find_elements
        (By.XPATH, "//*[@class='a-size-base review-text "
                   "review-text-content']")])

        # if there's a review from outside of country
        try:
            driver.find_elements(By.XPATH, "//*["
                                           "@data-hook='cmps-review-star-rating']")[
                0]

        except:
            pass

        else:
            loop = loop - len([i for i in driver.find_elements
            (By.XPATH, "//*[@data-hook='cmps-review-star-rating']")])

        try:
            # maximum #of review is 10 ea, but there're 2 on top as summary
            driver.find_element(By.ID, "cm_cr-rvw_summary-viewpoints")

        except:
            for j in range(loop):
                # if there's no summary on page
                reviewer = driver.find_elements(By.XPATH,
                                                "//*["
                                                "@class='a-profile-name']")[
                    j].text
                review_date = driver.find_elements(By.XPATH,
                                                   "//*[@data-hook='review-date']")[
                    j].text.replace(
                    "に日本でレビュー済み", "")
                review_score = driver.find_elements(By.XPATH,
                                                    "//*[@data-hook='review-star-rating']")[
                    j].get_attribute("textContent") \
                    .replace("5つ星のうち", "")
                review_title = driver.find_elements(By.XPATH,
                                                    "//*[@data-hook='review-title']")[
                    j].text
                review_content = driver.find_elements(By.XPATH,
                                                      "//*[@data-hook='review-body']")[
                    j].text.replace(
                    "\n", "")
                ASIN.append(asin)
                product.append(asin_name)
                brand.append(brand_name)
                name.append(reviewer)
                date.append(review_date)
                score.append(review_score)
                title.append(review_title)
                comment.append(review_content)
                # count += 1
                # if j == loop:
                #     next_page = find_next_page()
                #     if next_page is False:
                #         break
                #     else:
                #         pass

        else:

            for j in range(loop):
                reviewer = driver.find_elements(By.XPATH,
                                                "//*[@class='a-profile-name']")[
                    j + 2].text
                review_date = driver.find_elements(By.XPATH,
                                                   "//*[@data-hook='review-date']")[
                    j].text.replace(
                    "に日本でレビュー済み", "")
                review_score = driver.find_elements(By.XPATH,
                                                    "//*[@data-hook='review-star-rating']")[
                    j].get_attribute("textContent") \
                    .replace("5つ星のうち", "")
                review_title = driver.find_elements(By.XPATH,
                                                    "//*[@data-hook='review-title']")[
                    j + 2].text
                review_content = driver.find_elements(By.XPATH,
                                                      "//*[@data-hook='review-body']")[
                    j].text.replace(
                    "\n", "")
                ASIN.append(asin)
                product.append(asin_name)
                brand.append(brand_name)
                name.append(reviewer)
                date.append(review_date)
                score.append(review_score)
                title.append(review_title)
                comment.append(review_content)

        next_page = find_next_page()
        if next_page is False:
            break
        else:
            pass


def get_url(ASIN):
    """Connect to ASIN Detail Page on Chromedriver"""
    asin = "".join(ASIN)
    url = f"https://www.amazon.co.jp/dp/{asin}/"

    driver.get(url)
    driver.implicitly_wait(10)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located)

    review_page = driver.find_element(By.XPATH, "//*["
                                                "@data-hook='see-all-reviews-link-foot']")
    review_page.click()
    driver.implicitly_wait(10)


def get_data(csv):
    items = []
    for l in open(csv):
        items.append(l)

    num_items = len(items)
    for i, line in enumerate(open(csv)):
        progress = int(i / num_items * 100)
        print(f'Getting results...: {progress}%', end='\r')
        yield line.strip().split(",")
    print()


def make_list(l):
    output_data = "\n".join(",".join(i) for i in l)
    return output_data


def write_csv(output_data, filename):
    os.chdir(f'{output_dir_path}')
    with open(filename, "w") as f:
        f.write(output_data)
    df = pd.read_csv(filename, encoding="utf_8", header=None, names=columns)
    df.to_csv(filename)
    os.chdir(input_dir_path)


os.chdir(input_dir_path)
for i in get_data(asin_file):
    asin = "".join(i)
    try:
        get_url(i)
    except:
        print("No review on this ASIN")
    else:
        scraping_review(asin)
    #    filename = f"{asin}_{asin_name}_review_{today}.csv"

    final_data = [ASIN, product, brand, name, date, score, title, comment]
    print(final_data)
    summed_file = f'reviews_{month}.csv'
    try:
        df = pd.read_csv(f'{output_dir_path}/{summed_file}',
                         encoding="utf_8",
                         header=None, names=columns, skiprows=1)
        # print("ccc")
    except:
        df = pd.DataFrame(columns=columns)

    finally:
        df_add = pd.DataFrame(columns=columns)
        for clname, data in zip(columns, final_data):
            df_add[clname] = data
            # print("eee")

        # df_add["ASIN"] = ASIN
        # df_add["product"] = product
        # df_add["brand"] = brand
        # df_add["name"] = name
        # df_add["date"] = date
        # df_add["score"] = score
        # df_add["title"] = title
        # df_add["comment"] = comment

        print("bbb")
        combined_csv = pd.concat([df, df_add])
        combined_csv.to_csv(f'{output_dir_path}/{summed_file}')
        print(asin)

        ASIN = []
        product = []
        brand = []
        name = []
        date = []
        score = []
        title = []
        comment = []

driver.close()
print('Done scraping')
