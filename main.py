import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
import time
import webbrowser
from datetime import datetime

# enter venv first: source env/Scripts/activate

exclude_terms = ["senior", "lead", "manager", "principal", "staff"]

def scrape_deltamath(driver):
    wait = WebDriverWait(driver, 5)
    roles_list_visible = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/main/div/h2")))
    result = driver.find_element(By.XPATH, "/html/body/div/div[1]/main/div/p").text
    return result

def scrape_cambium(driver):
    wait = WebDriverWait(driver, 5)
    jobs_list = []
    page_loaded = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "MuiPagination-ul")))
    # because this often had pagination
    pagination = driver.find_element(By.CLASS_NAME, "MuiPagination-ul")
    buttons = pagination.find_elements(By.XPATH, "./*")
    has_pagination = len(buttons) > 0
    page = 1
    # for each page, append job items to jobs_list. Then click "next" button.
    while True:
        try: 
            list = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div[1]/div/ul")))
            items = list.find_elements(By.TAG_NAME, "li")
        except:
            break
        for item in items:
            try:
                text = item.text
                title = item.text.split("\n")[0]
                location = item.text.split("\n")[1]
                jobs_list.append(f"{title} - {location}")
            except Exception as e:
                continue
        if not has_pagination:
            break
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Go to next page']")))
            next_button.click()
            page += 1
        except:
            # print("No more pages")
            break

    jobs_list = [job for job in jobs_list if not any(term in job.lower() for term in exclude_terms)]
     
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

all_results = {}

for site in website_list:
    driver.get(site["url"])
    try:
        results = site["scraper"](driver)
        # if type(results) == list:
        #     print(f"{site['name']} results: ")
        #     for job in results:
        #         print(job)
        # else:
        #     print(f"{site['name']} results: {results}")

        # print("-" * 10)

        all_results[site['name']] = {
            'jobs': results if isinstance(results, list) else [results],
            'url': site['url']
        }
    except Exception as e:
        # print(f"Error with {site['name']}: {e}")
        all_results[site['name']] = {
            'jobs': [f"Errof: {e}"],
            'url': site['url']
        }
        
driver.quit()


