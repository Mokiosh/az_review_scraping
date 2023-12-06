"""This is a scraping program for each ASIN review"""

import datetime
import os
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


today = datetime.datetime.today().strftime("%Y%m%d")
options = Options()
options.add_argument('--incognito')
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

input_dir_path = 'az_review_scr/input_dir'
output_dir_path = 'az_review_scr/output_dir'
asin_file = 'review_ASIN.csv'
columns = ["name", "date", "score", "title", "comment"]


def scroll_down():
    """Get height of the page, and scroll down by loop"""
    height = driver.execute_script("return document.body.scrollHeight")
    half_height = height // 2
    for x in range(1, half_height):
        driver.execute_script("window.scrollTo(0, " + str(x) + ");")


def find_next_page():
    try:
        driver.find_element_by_xpath(
            "//*[@class='a-disabled a-last']")
        # no_next_page.click()
        return False
    except:
        next_page = driver.find_element_by_class_name("a-last")
        next_page.click()
        driver.implicitly_wait(10)
        return True


def scraping_review():
    review_count = int(driver.find_element_by_xpath(
        "//*[@data-hook='total-review-count']").text.replace(
        " 件のグローバル評価", "").replace(",", ""))
    asin_name = driver.find_element_by_class_name(
        "a-list-item").text.replace("...", "").replace("/", "")

    l_reviews = []
    while True:
        driver.implicitly_wait(10)
        scroll_down()
        for i in range(12):
            l = []
            if review_count > 50:
                try:
                    reviewer = driver.find_elements_by_class_name(
                        "a-profile-name")[i+2].text
                    review_date = driver.find_elements_by_xpath(
                        "//*[@data-hook='review-date']")[i+2].text.replace(
                        "に日本でレビュー済み", "")
                    review_score = driver.find_elements_by_xpath(
                        "//*[@data-hook='review-star-rating']")[
                        i+2].get_attribute("textContent") \
                        .replace("5つ星のうち", "")
                    review_title = driver.find_elements_by_xpath(
                        "//*[@data-hook='review-title']")[i+2].text
                    review_content = driver.find_elements_by_xpath(
                        "//*[@data-hook='review-body']")[i+2].text.replace(
                        "\n", "")
                    l.append(reviewer)
                    l.append(review_date)
                    l.append(review_score)
                    l.append(review_title)
                    l.append(review_content)
                    l_reviews.append(l)
                except IndexError:
                    print('No more reviews on this page', end='\r')
                    pass

            else:
                try:
                    reviewer = driver.find_elements_by_class_name(
                        "a-profile-name")[i].text
                    review_date = driver.find_elements_by_xpath(
                        "//*[@data-hook='review-date']")[i].text.replace(
                        "に日本でレビュー済み", "")
                    review_score = driver.find_elements_by_xpath(
                        "//*[@data-hook='review-star-rating']")[
                        i].get_attribute("textContent").replace("5つ星のうち", "")
                    review_title = driver.find_elements_by_xpath(
                        "//*[@data-hook='review-title']")[i].text
                    review_content = driver.find_elements_by_xpath(
                        "//*[@data-hook='review-body']")[i].text.replace(
                        "\n", "")
                    l.append(reviewer)
                    l.append(review_date)
                    l.append(review_score)
                    l.append(review_title)
                    l.append(review_content)
                    l_reviews.append(l)

                except IndexError:
                    print('No more reviews on this page', end='\r')
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

    review_page = driver.find_element_by_xpath(
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
    os.chdir(f'../../{output_dir_path}')
    with open(filename, "w") as f:
        f.write(output_data)
    df = pd.read_csv(filename, encoding="utf_8", header=None, names=columns)
    df.to_csv(filename)
    os.chdir(f'../../{input_dir_path}')


os.chdir(input_dir_path)
for i in get_data(asin_file):
    asin = "".join(i)
    get_url(i)
    review_data, asin_name = scraping_review()
    output_data = make_list(review_data)
    filename = f"{asin}_{asin_name}_review_{today}.csv"
    write_csv(output_data, filename)


driver.close()
print('Done scraping')
