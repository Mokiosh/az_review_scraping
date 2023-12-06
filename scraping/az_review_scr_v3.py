"""This is a scraping program for each ASIN review"""

import csv
import datetime
import os
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

today = datetime.datetime.today().strftime("%Y%m%d")
options = Options()
options.add_argument('--incognito')
# options.add_argument('--headless')
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

input_dir_path = '../input_dir'
output_dir_path = '../output_dir'
asin_file = 'review_ASIN.csv'
done_ASIN_list_name = f"{today}_done_ASIN.csv"
columns = ["ASIN", "product", "variant", "brand", "name", "date", "score",
           "title", "comment"]


def scroll_down():
    """Get height of the page, and scroll down by loop"""
    height = driver.execute_script("return document.body.scrollHeight")
    half_height = height // 1
    for x in range(1, half_height):
        driver.execute_script("window.scrollTo(0, " + str(x) + ");")


def find_next_page():
    try:
        driver.find_element(By.XPATH,
            "//*[@class='a-disabled a-last']")
        # no_next_page.click()
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
    global IndexError
    asin_name = driver.find_element(By.CLASS_NAME,
        "a-list-item").text.replace("...", "").replace("/", "")
    brand = driver.find_element(By.ID, "cr-arp-byline").text

    l_reviews = []
    while True:
        driver.implicitly_wait(10)
        scroll_down()

        # maximum #of review is 10 ea, but there're 2 on top as summary
        try:
            driver.find_element(By.ID, "cm_cr-rvw_summary-viewpoints")
            # print("There's a summary")
            for i in range(10):
                l = []
                try:
                    variant = driver.find_element(By.XPATH,
                        "//*[@class='a-size-mini a-link-normal "
                        "a-color-secondary']")[
                        i].text
                except:
                    variant = ""

                try:
                    reviewer = driver.find_element(By.XPATH,
                        "//*[@data-hook='genome-widget']")[i + 2].text
                    review_date = driver.find_element(By.XPATH,
                        "//*[@data-hook='review-date']")[i].text.replace(
                        "に日本でレビュー済み", "")
                    review_score = driver.find_element(By.XPATH,
                        "//*[@data-hook='review-star-rating']")[
                        i].get_attribute("textContent") \
                        .replace("5つ星のうち", "")
                    review_title = driver.find_element(By.XPATH,
                        "//*[@data-hook='review-title']")[i + 2].text
                    review_content = driver.find_element(By.XPATH,
                        "//*[@data-hook='review-body']")[i].text.replace(
                        "\n", "")
                    l.append(asin)
                    l.append(asin_name)
                    l.append(brand)
                    l.append(variant)
                    l.append(reviewer)
                    l.append(review_date)
                    l.append(review_score)
                    l.append(review_title)
                    l.append(review_content)
                    l_reviews.append(l)
                except:
                    pass


                # print(i)

        except:
            # if there's no summary on page
            # print("no summary")
            for i in range(10):
                l = []
                try:
                    variant = driver.find_element(By.XPATH,
                        "//*[@class='a-size-mini a-link-normal "
                        "a-color-secondary']")[
                        i].text
                except:
                    variant = ""

                try:
                    reviewer = driver.find_element(By.XPATH,
                        "//*[@data-hook='genome-widget']")[i].text
                    review_date = driver.find_element(By.XPATH,
                        "//*[@data-hook='review-date']")[i].text.replace(
                        "に日本でレビュー済み", "")
                    review_score = driver.find_element(By.XPATH,
                        "//*[@data-hook='review-star-rating']")[
                        i].get_attribute("textContent").replace("5つ星のうち", "")
                    review_title = driver.find_element(By.XPATH,
                        "//*[@data-hook='review-title']")[i].text
                    review_content = driver.find_element(By.XPATH,
                        "//*[@data-hook='review-body']")[i].text.replace(
                        "\n", "")
                    l.append(asin)
                    l.append(asin_name)
                    l.append(brand)
                    l.append(variant)
                    l.append(reviewer)
                    l.append(review_date)
                    l.append(review_score)
                    l.append(review_title)
                    l.append(review_content)
                    l_reviews.append(l)

                except:
                    pass



        next_page = find_next_page()
        if next_page is False:
            break
        else:
            pass

    return l_reviews, asin_name


def get_url(ASIN):
    """Connect to ASIN Detail Page on Chromedriver"""
    asin = "".join(ASIN)
    url = f"https://www.amazon.co.jp/dp/{asin}/"

    driver.get(url)
    driver.implicitly_wait(10)
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located)

    review_page = driver.find_element(By.XPATH,
        "//*[@data-hook='see-all-reviews-link-foot']")
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


def convert_1d_to_2d(l, cols):
    return [l[i:i + cols] for i in range(0, len(l), cols)]


os.chdir(output_dir_path)
items = []
try:
    for m in open(done_ASIN_list_name):
        items.append(m)
        # print(items)
except:
    pass

os.chdir(input_dir_path)
for i in get_data(asin_file):
    asin = "".join(i)
    try:
        get_url(i)
    except:
        print(f'no review on {asin}')
    else:
        review_data, asin_name = scraping_review(asin)
        output_data = make_list(review_data)
        asin_name = asin_name.replace("　", "_")
        filename = f"{asin}_{asin_name}_review_{today}.csv"
        write_csv(output_data, filename)

        # make asin list to combine reviews later
        os.chdir(output_dir_path)
        items.append(filename)
        final_items = convert_1d_to_2d(items, 1)
        print(f'Done {filename}')

        with open(done_ASIN_list_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(final_items)
        os.chdir(input_dir_path)

driver.close()
print('Done scraping')
