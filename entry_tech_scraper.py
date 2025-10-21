from selenium.webdriver.chrome.options import Options
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
import time
import webbrowser
from datetime import datetime
import os
from object_methods import BaseMethods
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any

job_titles =[
    "qa tester", "qa engineer", "technical support engineer", 
]

# scan the description for years of experience to cut out some

# make this one object methods

website_list: [
    # zensearch, 
]

class WebScraper(ABC):
    def __init__(self, driver: webdriver.Chrome, default_timeout=3):
        self.driver = driver
        self.default_timeout = default_timeout
        self.url = self.get_url()

    @property
    def wait(self):
        return WebDriverWait(self.driver, self.default_timeout)
    
    def get_wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.default_timeout)
        # Use this one when using a custom timeout

    @abstractmethod
    def get_url(self) -> str:
        # will pass the url to be scraped
        pass
    
    @abstractmethod
    def scrape(self):
        # end result: description(str), href(str)
        pass

    @abstractmethod
    def get_company(self) -> str:
        pass

    def navigate(self):
        self.driver.get(self.url)

class ScrapeCUofCO(WebScraper):
    def get_url(self):
        return "https://www.ccu.org/about/careers"
    
    def scrape(self):
        # locator_jobs_shown_toggle = (By.ID, "show-records-top")
        locator_results = (By.CSS_SELECTOR, "#results li.JobInfo")
        self.navigate()
        wait = self.get_wait()
        time.sleep(3)
        jobs_list = self.wait.until(EC.presence_of_all_elements_located(locator_results))
        for job in jobs_list:
            print(job.text)
        return "text1"

class ScrapeXcel(WebScraper):
    def get_company(self):
        return "Xcel Energy"

    def get_url(self):
        return "https://jobs.xcelenergy.com/technology-services"
    
    def scrape(self):
        locator = (By.CLASS_NAME, "results-list")
        self.navigate()
        jobs_list = self.wait.until(EC.visibility_of_all_elements_located(locator))
        for job in jobs_list:
            print(job.text)
        return "test2"

class ScraperManager:
    def __init__(self):
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)
        self.scrapers: List[WebScraper] = []

    def register_scraper(self, scraper_class: type[WebScraper]):
        self.scrapers.append(scraper_class(self.driver))

    def run_all(self):
        results = []
        for scraper in self.scrapers:
            try:
                print(f"Now scraping: {scraper.get_company()}")
                result = scraper.scrape()
                results.append(result)
            except Exception as e:
                print(f"Error scraping {scraper.get_company()}: {e}")
        return results
    
    def cleanup(self):
        self.driver.quit()

if __name__ == "__main__":
    manager = ScraperManager()

    # manager.register_scraper(ScrapeCUofCO)
    manager.register_scraper(ScrapeXcel)

    results = manager.run_all()

    print("Results:", "\n", results)

    manager.cleanup()