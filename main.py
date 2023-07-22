# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm


class Cafe:
    def __init__(self, name, address, review, photoUrlList):
        self.name = name
        self.address = address
        self.review = review
        self.photoUrlList = photoUrlList

    def __str__(self):
        return self.name + "\n" + self.address + "\n" + "\n----------------------------------------------------------------------------------------\n".join(self.review) + "\n" + "\n".join(self.photoUrlList) + "\n===========================================================================\n"

    def fromUrl(url, driver):
        driver.get(url)
        driver.implicitly_wait(3)

        name = driver.find_element(By.CLASS_NAME, "restaurant_name").text
        address = driver.find_element(By.CSS_SELECTOR, "body > main > article > div.column-wrapper > div.column-contents > div > section.restaurant-detail > table > tbody > tr:nth-child(1) > td").text.split("\n")[0].strip()
        
        photoUrlList = driver.find_elements(By.CLASS_NAME, "restaurant-photos-item")

        photoUrlList = [photoUrl.find_element(By.CLASS_NAME, "center-croping").get_attribute("src") for photoUrl in photoUrlList]

        num_revew = int(driver.find_element(By.CLASS_NAME, "RestaurantReviewList__AllCount").text)

        for i in range(num_revew//5-1):
            driver.find_element(By.CLASS_NAME, "RestaurantReviewList__MoreReviewButton").click()

        review = list(map(lambda x: x.text.replace("\n", " "), driver.find_elements(By.CLASS_NAME, "RestaurantReviewItem__ReviewText")))

        return Cafe(name, address, review, photoUrlList)
    
    # class to dict
    def to_dict(self):
        return self.__dict__
        



options = Options()

#지정한 user-agent로 설정합니다.
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
options.add_argument('user-agent=' + user_agent)
options.add_argument("--log-level=3")
options.add_argument('headless') #headless모드 브라우저가 뜨지 않고 실행됩니다.
options.add_argument('--blink-settings=imagesEnabled=false') #브라우저에서 이미지 로딩을 하지 않습니다.




# Chrome WebDriver를 이용해 Chrome을 실행합니다.
driver = webdriver.Chrome(options=options)

driver.get("https://www.mangoplate.com/search/%EA%B0%95%EB%82%A8%20%EC%B9%B4%ED%8E%98?keyword=%EA%B0%95%EB%82%A8%20%EC%B9%B4%ED%8E%98&page=1")
driver.implicitly_wait(3)

idList = []

for i in tqdm(range(10)):
    driver.get(f'https://www.mangoplate.com/search/%EA%B0%95%EB%82%A8%20%EC%B9%B4%ED%8E%98?keyword=%EA%B0%95%EB%82%A8%20%EC%B9%B4%ED%8E%98&page={1+i}')
    driver.implicitly_wait(3)
    idList += [driver.find_element(By.XPATH, f'/html/body/main/article/div[2]/div/div/section/div[3]/ul/li[{(i-1)//2+1}]/div[{2-i%2}]/figure/figcaption/div/a').get_attribute("href").split("/")[-1] for i in range(1, 11)]
print(len(idList))


cafeList = []

for i, cafeId in tqdm(enumerate(idList)):
    cafe = Cafe.fromUrl(f'https://www.mangoplate.com/restaurants/{cafeId}', driver)
    driver.implicitly_wait(3)
    cafeList.append(cafe.__dict__)
    time.sleep(1)

# cafeList를 json파일로 저장
import json
with open('cafeList.json', 'w', encoding='utf-8') as f:
    json.dump(cafeList, f, ensure_ascii=False, indent=4)

# WebDriver를 종료합니다. (브라우저 닫기)
driver.quit()