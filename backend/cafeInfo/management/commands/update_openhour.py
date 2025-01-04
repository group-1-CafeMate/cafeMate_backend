from django.core.management.base import BaseCommand

from cafeInfo.models import Cafe, OperatingHours
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from webdriver_manager.chrome import ChromeDriverManager
from time import sleep


class Command(BaseCommand):
    help = "update open hours of cafe"

    def handle(self, *args, **kwargs):
        # driver = webdriver.Firefox()
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        service = Service(executable_path=ChromeDriverManager().install())
        # 啟動瀏覽器
        driver = webdriver.Chrome(service=service, options=options)
        try:
            cafes = Cafe.objects.filter(legal=True)
            for c in cafes:
                driver.get(c.gmap_link)
                wait = WebDriverWait(driver, 10)
                try:
                    table = wait.until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, "table.eK4R0e tbody")
                        )
                    )
                except TimeoutException:
                    print(f"Timeout while loading table for {c.name}. Skipping.")
                    continue

                soup = BeautifulSoup(table.get_attribute("innerHTML"), "html.parser")

                business_hours = {}

                # 查找所有<tr>標籤
                rows = soup.find_all("tr", class_="y0skZc")

                for row in rows:
                    # 提取星期
                    day = row.find("td", class_="ylH6lf").get_text(strip=True)

                    # 提取營業時間
                    time = row.find("li", class_="G8aQO").get_text(strip=True)

                    # 將結果存入字典
                    if day not in business_hours:
                        business_hours[day] = ""
                    business_hours[day] = time

                OperatingHours.objects.filter(cafe=c).delete()
                for day, hours in business_hours.items():
                    if hours == "休息":
                        open_time = "休息"
                        close_time = "休息"
                    else:
                        open_time, close_time = hours.split("–")

                    OperatingHours.objects.create(
                        cafe=c,
                        day_of_week=day,
                        open_time=open_time,
                        close_time=close_time,
                    )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))
        driver.quit()
