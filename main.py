import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
import time

# enter venv first: source env/Scripts/activate

def scrape_deltamath(driver):
    wait = WebDriverWait(driver, 5)
    roles_list_visible = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/main/div/h2")))
    result = driver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/p").text
    return result

def scrape_cambium(driver):
    wait = WebDriverWait(driver, 5)
    list = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div[1]/div/ul")))
    items = list.find_elements(By.TAG_NAME, "li")
    jobs_list = []
    for item in items:
        title = item.text.split("\n")[0]
        location = item.text.split("\n")[1]
        jobs_list.append(f"{title} - {location}")
    return jobs_list

website_list = [
    {"url": "https://www.deltamath.com/jobs/",
     "name": "DeltaMath",
     "scraper": scrape_deltamath},
     {"url": "https://jobs.cambiumlearning.com/?size=n_5_n/",
      "name": "Cambium Learning Group",
      "scraper": scrape_cambium}
]

driver = webdriver.Chrome()

for site in website_list:
    driver.get(site["url"])
    try:
        results = site["scraper"](driver)
        if type(results) == list:
            print(f"{site['name']} results: ")
            for job in results:
                print(job)
        else:
            print(f"{site['name']} results: {results}")

        print("-" * 10)
    except Exception as e:
        print(f"Error with {site['name']}: {e}")

    

driver.quit()
