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
from typing import List, Dict, Any

JobList = List[Dict[str, str]]

# enter venv first: source env/Scripts/activate

excluded_terms = ["senior", "lead", "manager", "principal", "staff", "director", "chief", "teacher", "sr", "architect", "head", "business intelligence", "therapist", "director", "president", "sales", "counsel", "vp"]

acceptable_locations =[
        "remote" , "denver" , "co" , "colorado" , "united states" , "usa" , "us", ""
    ]

excluded_locations = [
    "india", "telugu", "odisha", "karnataka", "delhi"
]

# General helpers---------------------------------------------
def click_element(locator, driver, time = 3):
    WebDriverWait(driver, time).until(EC.element_to_be_clickable(locator)).click()

def type_in_element(locator, text, time = 2):
    WebDriverWait(driver, time).until(EC.element_to_be_clickable(locator)).send_keys(text)

def get_wait(driver, timeout=3):
    return WebDriverWait(driver, timeout)

def check_for_button_next(driver, locator):
    wait = get_wait(driver)
    try:
        wait.until(EC.element_to_be_clickable(locator)).click()
        return True
    except:
        print("No next button present")
        return False

def infinite_scroll(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        scrollToBottom()
        # time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def jobs_title_check(jobs_list, excluded_terms=excluded_terms):
    jobs_list[:] = [
        job for job in jobs_list 
        if not any(term in job.lower() for term in excluded_terms)
    ]

def jobs_title_check_with_key(jobs_list, key, excluded_terms=excluded_terms):
        jobs_list[:] = [
        job for job in jobs_list 
        if not any(term in job[key].lower() for term in excluded_terms)
    ]

def parse_job_info(jobs):
    temp_jobs_list = []
    for job in jobs:
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[1] if len(lines) > 1 else ""
        pay = lines[2] if len(lines) > 2 else ""
        if "Future Opportunities" in title:
            break
        # if "remote" in job.text.split("\n")[1].lower():
        #     location = "Remote"
        temp_jobs_list.append(f"{title} - {location} - {pay}")
    jobs_title_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def parse_job_info_with_link_text(job, job_entry):
    lines = job.text.split("\n")
    title = lines[0]
    location = lines[1] if len(lines) > 1 else ""
    job_entry["description"] = f"{title} - {location}"

def add_href_to_job_entry(job, job_entry):
    try:
        if job.get_attribute("href"):
            job_entry['href'] = job.get_attribute("href")
        elif job.find_element(By.TAG_NAME, "a"):
            link_element = job.find_element(By.TAG_NAME, "a")
            job_entry['href'] = link_element.get_attribute("href")
    except Exception:
        job_entry['href'] = None

def parse_job_info_with_link(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        job_entry = {}
        parse_job_info_with_link_text(job, job_entry)
        add_href_to_job_entry(job, job_entry)
        temp_jobs_list.append(job_entry)
    jobs_aggregator_list_check(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list

def jobs_aggregator_list_check(jobs_list, key, excluded_terms=excluded_terms):
    jobs_list[:] = [
        job for job in jobs_list 
        if not any(term in job[key].lower() for term in excluded_terms)
    ]
    jobs_list[:] = [
        job for job in jobs_list 
        if any(re.search(r'\b' + re.escape(term) + r'\b', job[key].lower())
               for term in acceptable_locations)
    ]

    #     # Debugging---------------------------
    # deleted_by_terms = [
    #     job for job in jobs_list 
    #     if any(term in job[key].lower() for term in excluded_terms)
    # ]
    # deleted_by_location = [
    #     job for job in jobs_list 
    #     if not any(re.search(r'\b' + re.escape(term) + r'\b', job[key].lower())
    #            for term in acceptable_locations)
    # ]
    # if deleted_by_terms:
    #     print(f"\n---- Deleted by excluded terms ({len(deleted_by_terms)}): ----")
    #     for job in deleted_by_terms:
    #         print(f"  - {job[key]}")
    # if deleted_by_location:
    #     print(f"\n---- Deleted by location filter ({len(deleted_by_location)}): ----")
    #     for job in deleted_by_location:
    #         print(f"  - {job[key]}")

def parse_aggregator_info(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        job_entry = {}
        lines = job.text.split("\n")
        title = lines[0]
        company = lines[1]
        location = lines[2]
        salary = lines[4]
        job_entry["description"] = f"{title} at {company} - {location} - {salary}"
        add_href_to_job_entry(job, job_entry)
        temp_jobs_list.append(job_entry)
    jobs_aggregator_list_check(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list

def check_location(location, title):
    if not any(term in location.lower() for term in acceptable_locations):
        return False
    if ("telugu") in title.lower():
        return False
    if any(term in location.lower() for term in excluded_locations):
        return False
    return True

def scrollToBottom():
    footer_locator = (By.CSS_SELECTOR, "footer")
    wait = get_wait(driver)
    footer_element = wait.until(EC.presence_of_element_located(footer_locator))
    time.sleep(2)
    driver.execute_script("arguments[0].scrollIntoView()", footer_element)
    time.sleep(2)

def check_for_iframes(driver):
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    print("Found iframes:", len(iframes))

def deal_with_iframes(driver, frame_index):
    locator_iframe = (By.TAG_NAME, "iframe")
    wait = get_wait(driver)
    iframes = wait.until(EC.presence_of_all_elements_located(locator_iframe))
    driver.switch_to.frame(iframes[frame_index])


# Parsers - site specific----------------------------

def parse_job_info_edtechjobsio(jobs):
    temp_jobs_list = []    
    for job in jobs:
        job_entry = {}
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        company = lines[1] if len(lines) > 1 else ""
        location = lines[5] if len(lines) > 5 else ""
        pay = ""
        if len(lines) > 7 and "ago" in lines[7]:
            posted = lines[7]
        elif len(lines) > 7:
            pay = lines[7]
            posted = lines[9] if len(lines) > 9 else ""
        if ("min" or "h" or "d" or "w" in posted) and ("Sales" not in title):
            job_entry['description'] = f"{title} - {company} - {location} - {pay} - {posted}"
            try:
                link_el = job.find_element(By.CSS_SELECTOR, "a.job-details-link")
                job_entry['href'] = link_el.get_attribute("href")
            except Exception:
                job_entry['href'] = None
            temp_jobs_list.append(job_entry)
    jobs_aggregator_list_check(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list

def collect_multipage_edtechio(driver, url, locator, job_listings):
    wait = get_wait(driver)
    driver.get(url)
    temp_job_listings = wait.until(EC.presence_of_all_elements_located(locator))
    job_listings += parse_job_info_edtechjobsio(temp_job_listings)
    return job_listings

def parse_khan_academy(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        job_entry = {}
        lines = job.text.split("\n")
        title = lines[0]
        location = lines[1] if len(lines) > 1 else ""
        if not any(term in location.lower() for term in acceptable_locations):
            print(location)
        job_entry["description"] = f"{title} - {location}"
        if (not check_location(location, title)) or ("talent community" in title.lower()):
            continue
        add_href_to_job_entry(job, job_entry)
        temp_jobs_list.append(job_entry)
    jobs_aggregator_list_check(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list
        
def parse_savvas(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[1] if len(lines) > 1 else ""
        if check_location(location, title) == False:
            continue
        temp_jobs_list.append(f"{title} - {location}")
    jobs_title_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def parse_macmillan(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[5] if len(lines) > 1 else ""
        location2 = lines[10] if len(lines) > 2 else ""
        temp_jobs_list.append(f"{title} - {location} - {location2}")
    jobs_title_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list

def parse_mgcraw_hill(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        job_entry = {}
        lines = job.text.split("\n")
        title = lines[0]
        location = lines[6]
        job_entry["description"] = f"{title} - {location}"
        add_href_to_job_entry(job, job_entry)
        temp_jobs_list.append(job_entry)
    jobs_title_check_with_key(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list

def parse_greatMinds(jobs_list):
    temp_jobs_list = []
    row_header = "Job title Work model Location"
    for job in jobs_list:
        job_entry = {}
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        if row_header not in title:
            job_entry['description'] = title
            try:
                link_el = job.find_element(By.TAG_NAME, "a")
                href = link_el.get_attribute('href')
                job_entry['href'] = href
            except Exception:
                job_entry['href'] = None
            temp_jobs_list.append(job_entry)
    jobs_title_check_with_key(temp_jobs_list, "description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def parse_jeffco(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        job_entry = {}
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[2] if len(lines) > 1 else ""
        job_entry["description"] = f"{title} - {location}"
        temp_jobs_list.append(job_entry)
    jobs_aggregator_list_check(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def parse_imagine_learning(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        job_entry = {}
        lines = job.text.split("\n")
        title = lines[0]
        location = lines[1]
        job_entry["description"] = f"{title} - {location}"
        add_href_to_job_entry(job, job_entry)
        temp_jobs_list.append(job_entry)
    jobs_aggregator_list_check(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list

def parse_blackbaud(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        job_entry = {}
        lines = job.text.split("\n")
        title = lines[0]
        location = lines[2]
        job_entry["description"] = f"{title} - {location}"
        add_href_to_job_entry(job, job_entry)
        temp_jobs_list.append(job_entry)
    jobs_aggregator_list_check(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list

def parse_collegeboard(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        job_entry = {}
        parse_job_info_with_link_text(job, job_entry)
        add_href_to_job_entry(job, job_entry)
        temp_jobs_list.append(job_entry)
    jobs_title_check_with_key(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list

# Scrapers-----------------------------------------

def scrape_abre(driver) -> JobList:
    locator = (By.XPATH, "/html/body/main/section[2]/div[2]/div/ul/li")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_job_info_with_link(jobs_list)

def scrape_adamscounty(driver) -> JobList:
    wait = get_wait(driver)
    return "Nothing posted for tech jobs in order to test scraper."

def scrape_adtalem(driver) -> JobList:
    locator = (By.CLASS_NAME, "attrax-vacancy-tile")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_job_info_with_link(jobs_list)

def scrape_anthology(driver):
    return "None, tech jobs only in India"

def scrape_blackbaud(driver) -> JobList:
    locator = (By.CLASS_NAME, "jobs-list-item")
    locator_next_button = (By.XPATH, "/html/body/div[2]/div[2]/section[6]/div/div/div[2]/div/div/section/div[5]/div/div[2]/div/div[4]/button[2]")
    wait = get_wait(driver)
    next_button = wait.until(EC.element_to_be_clickable(locator_next_button))
    next_button.click()
    time.sleep(3)
    jobs_list = wait.until(EC.visibility_of_all_elements_located(locator))
    return parse_blackbaud(jobs_list)

def scrape_cambium(driver) -> JobList:
    wait = get_wait(driver)
    jobs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div[1]/div/ul/li")))
    time.sleep(1)
    return parse_job_info_with_link(jobs)   

def scrape_collegeboard(driver) -> JobList:
    wait = get_wait(driver)
    job_listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul h3")))
    # has a page 2, but couldn't get it to load correctly
    return parse_collegeboard(job_listings)

def scrape_coloradodoe(driver) -> JobList:
    locator = (By.CLASS_NAME, "job-table-title")
    wait = get_wait(driver)
    job_listings = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_job_info_with_link(job_listings)

def scrape_coursera(driver) -> JobList:
    title_locator = (By.CSS_SELECTOR, ".job-search-results-title a")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(title_locator))
    return parse_job_info_with_link(jobs_list)

def scrape_curriculumAssociates(driver):
    return "None - all tech jobs in India"

def scrape_deltamath(driver) -> JobList:
    wait = get_wait(driver)
    roles_list_visible = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/main/div/p")))
    results = roles_list_visible.text
    return results

def scrape_dps_aurora(driver) -> JobList:
    wait = get_wait(driver)
    title_locator = (By.CSS_SELECTOR, "ul span.job-tile__title")
    jobs_tiles = wait.until(EC.presence_of_all_elements_located(title_locator))
    # can't pull hrefs since it is so many divs up. Tried several ways.
    return parse_job_info(jobs_tiles)

def scrape_edmentum(driver) -> JobList:
    return scrape_greenouse(driver)

def scrape_edtechcom(driver) -> JobList:
    locator = (By.CSS_SELECTOR, "#listings a")
    wait = get_wait(driver)
    scrollToBottom()
    time.sleep(2)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_aggregator_info(jobs_list)

def scrape_edtechjobsio(driver) -> JobList:
    url_entry_level = "https://edtechjobs.io/jobs/entry-level"
    url_curriculum = "https://edtechjobs.io/jobs/curriculum"
    url_software_search = "https://edtechjobs.io/jobs?filters%5B22579%5D=software&filters%5B22580%5D=&filters%5B22581%5D=&filters%5B22582%5D=7&filters%5B22583%5D%5Blocation%5D=&filters%5B22583%5D%5Blocation_id%5D=&filters%5B22583%5D%5Bsearch_radius%5D=&filters%5B22584%5D=1&order=relevance"
    locator_next_button = (By.CSS_SELECTOR, "[aria-label='Next »']")
    locator_job_list = (By.CLASS_NAME, "job-listings-item")
    job_listings = []

    wait = get_wait(driver)

    collect_multipage_edtechio(driver, url_entry_level, locator_job_list, job_listings)
    collect_multipage_edtechio(driver, url_curriculum, locator_job_list, job_listings)
    collect_multipage_edtechio(driver, url_software_search, locator_job_list, job_listings)
    if check_for_button_next(driver, locator_next_button):
        job_listings_software_2 = wait.until(EC.presence_of_all_elements_located(locator_job_list))
        job_listings += parse_job_info_edtechjobsio(job_listings_software_2)

    return job_listings

def scrape_goguardian(driver) -> JobList:
    # greenhouse
    locator = (By.CSS_SELECTOR, "tbody .cell")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_job_info_with_link(jobs_list)

def scrape_greatMinds(driver) -> JobList:
    list_locator = (By.XPATH, "/html/body/div/div[3]/main/div[2]/section/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[2]/div/output")
    jobs_locator = (By.TAG_NAME, "tr")
    wait = get_wait(driver)
    list = wait.until(EC.presence_of_element_located(list_locator))
    jobs_list = list.find_elements(*jobs_locator)
    return parse_greatMinds(jobs_list)

def scrape_greenouse(driver) -> JobList:
    locator = (By.CLASS_NAME, "job-post")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_job_info_with_link(jobs_list)

def scrape_guild(driver):
    # client side rendering makes this not work.
    return

def scrape_imagine_learning(driver) -> JobList:
    locator = (By.CSS_SELECTOR, ".jv-job-list li")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_imagine_learning(jobs_list)

def scrape_jeffco_schools(driver) -> JobList:
    locator_show_all_jobs = (By.ID, "HRS_SCH_WRK$0_row_0")
    locator_search_text_box = (By.XPATH, "/html/body/form/div[2]/div[4]/div[2]/div/div/div/div/div[2]/section/div/div[1]/div/div/div/div[1]/div[1]/div/div[2]/input")
    search_terms = "Office/Tech/Support Staff"
    locator_search_button = (By.ID, "HRS_SCH_WRK_FLU_HRS_SEARCH_BTN")
    locator_results_list = (By.CSS_SELECTOR, "div[title='Search Results List'] > ul > li")

    wait = get_wait(driver)
    click_element(locator_show_all_jobs, driver)
    type_in_element(locator_search_text_box, search_terms)
    click_element(locator_search_button, driver)
    time.sleep(1)
    jobs_list = driver.find_elements(*locator_results_list)  
    # no good way to get href from it, as it's a component update not a new url 
    return parse_jeffco(jobs_list)

def scrape_khan(driver) -> JobList:
    locator = (By.CLASS_NAME, "_12k2rikw")
    wait = get_wait(driver)
    jobs_list =  wait.until(EC.presence_of_all_elements_located(locator))
    return parse_khan_academy(jobs_list)

def scrape_macmillan(driver) -> JobList:
    locator = (By.CLASS_NAME, "opportunity")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_macmillan(jobs_list)

def scrape_magicschool(driver) -> JobList:
    wait = get_wait(driver)
    list_of_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ashby-job-posting-brief")))
    return parse_job_info(list_of_elements)

def scrape_mapleton(driver):
    return "Nothing posted for tech jobs in order to test scraper."

def scrape_masteryprep(driver) -> JobList:
    it_locator = (By.LINK_TEXT, "IT")
    jobs_locator = (By.CSS_SELECTOR, "li.whr-item")
    wait = get_wait(driver)
    wait.until(EC.element_to_be_clickable(it_locator)).click()
    time.sleep(1)
    jobs_list = wait.until(EC.presence_of_all_elements_located(jobs_locator))
    return parse_job_info_with_link(jobs_list)

def scrape_mcgraw_hill(driver) -> JobList:
    locator = (By.CLASS_NAME, "mat-expansion-panel")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.visibility_of_all_elements_located(locator))
    return parse_mgcraw_hill(jobs_list)

def scrape_newsela(driver) -> JobList:
    return scrape_greenouse(driver)

def scrape_noRedInk(driver) -> JobList:
    locator = (By.CSS_SELECTOR, ".opening")
    wait = get_wait(driver)
    deal_with_iframes(driver, 1)
    jobs_list = wait.until(EC.visibility_of_all_elements_located(locator))
    return parse_job_info_with_link(jobs_list)

def scrape_pairin(driver) -> JobList:
    wait = get_wait(driver)
    element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/section/div[6]/h4")))
    list_of_elements = driver.find_element(By.XPATH, "/html/body/div[1]/main/section/div[6]/h4")
    # NEED TO ADD SCRAPER FOR WHEN THERE IS A JOB TO TEST WITH
    return list_of_elements.text

def scrape_pearson(driver) -> JobList:
    modal_locator = (By.ID, "onetrust-accept-btn-handler")
    locator_jobs = (By.CSS_SELECTOR, "#main li")
    wait = get_wait(driver)
    modal_closer = wait.until(EC.element_to_be_clickable(modal_locator))
    modal_closer.click()
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator_jobs))
    return parse_job_info_with_link(jobs_list)

def scrape_powerschool(driver):
    return "None - all tech jobs are India"

def scrape_promethean(driver):
    return "None. tech and operations jobs are not US based."

def scrape_proximity_learning(driver) -> JobList:
    locator = (By.CLASS_NAME, "fabric-2orkpc-root")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_job_info_with_link(jobs_list)

def scrape_public_schools_workday(driver) -> JobList:
    wait = get_wait(driver)
    job_listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul h3")))
    return parse_job_info_with_link(job_listings)

def scrape_savvas(driver):
    locator = (By.CSS_SELECTOR, ".ant-list-items li")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_savvas(jobs_list)

def scrape_schoolai(driver):
    locator = (By.CLASS_NAME, "css-aapqz6")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_job_info_with_link(jobs_list)

def scrape_skyward(driver):
    locator = (By.CLASS_NAME, "opening-jobs")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_job_info(jobs_list)

def scrape_timely_schools(driver):
    deal_with_iframes(driver, 0)
    wait = get_wait(driver)
    locator = (By.XPATH, "/html/body/div/div[1]/div[2]/div[2]//a")
    jobs_list = wait.until(EC.visibility_of_all_elements_located(locator))
    return parse_job_info_with_link(jobs_list)

def scrape_turnitin(driver):
    infinite_scroll(driver)
    locator = (By.XPATH, "/html/body/div[1]/div/main/section[2]/div/div//a")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.visibility_of_all_elements_located(locator))
    jobs_list = parse_job_info_with_link(jobs_list)
    jobs_list[:] = [
        job for job in jobs_list 
        if re.search(r"\b(u\.?s\.?|usa)\b", job['description'], re.IGNORECASE)
    ]
    if len(jobs_list) == 0:
        jobs_list.append("None")
    return jobs_list

# debug: pearson, savvas, newsela
website_list = [
    # {"url": "",
    #  "name": "",
    #  "scraper": },
    # {"url": "https://www.applitrack.com/mapleton/onlineapp/default.aspx?all=1",
    #  "name": "Mapleton Public Schools", 
    #  "scraper": scrape_mapleton},
    # {"url": "https://www.applitrack.com/adams12/onlineapp/default.aspx?all=1",
    #  "name": "Adams County Schools",
    #  "scraper": scrape_adamscounty},
    # {"url": "https://scholastic.wd5.myworkdayjobs.com/External?jobFamilyGroup=b56865245e494669bad1614c8bd5e1bf&jobFamilyGroup=07ac9b2f73ee4662b9ebf744f4860a0f",
    #  "name": "Scholastic",
    #  "scraper": scrape_public_schools_workday},
    {"url": "https://careers.adtalem.com/jobs?options=217%2C204&page=1&size=50",
     "name": "Adtalem",
     "scraper": scrape_adtalem},
    # {"url": "https://cengage.wd5.myworkdayjobs.com/CengageNorthAmericaCareers?jobFamilyGroup=5cbb6d959a9e0174784c722a280adc5a&jobFamilyGroup=5cbb6d959a9e0169db1a6f2a280ad45a",
    #  "name": "Cengage",
    #  "scraper": scrape_public_schools_workday},
    #  {"url": "https://careers.mheducation.com/jobs?page=1&locations=,,United%20States&tags2=Remote&categories=Technology&limit=100",
    #  "name": "McGraw Hill",
    #  "scraper": scrape_mcgraw_hill},
    # {"url": "https://collegeboard.wd1.myworkdayjobs.com/en-US/Careers?locations=5d2a8b008de5013111b33268b9008210",
    #  "name": "College Board", 
    #  "scraper": scrape_collegeboard},
    # {"url": "https://careers.smartrecruiters.com/TurnitinLLC",
    #  "name": "Turnitin",
    #  "scraper": scrape_turnitin},
    # {"url": "https://www.timelyschools.com/careers",
    #  "name": "Timely Schools",
    #  "scraper": scrape_timely_schools},
    # {"url": "https://careers.blackbaud.com/us/en?_gl=1*andnev*_gcl_au*MTE3NjM2Njg3Mi4xNjg3NDU5Nzk1&_ga=2.179888804.1463122241.1687459796-541182962.1687459796",
    #  "name": "Blackbaud",
    #  "scraper": scrape_blackbaud},
    # {"url": "https://www.noredink.com/about/jobs/",
    #  "name": "NoRedInk",
    #  "scraper": scrape_noRedInk},
    # {"url": "https://ats.rippling.com/schoolai/jobs?fbp=fb.1.1748892812325.371522121602605846&searchQuery=&workplaceType=&country=US&state=&city=&page=0&pageSize=20",
    #  "name": "SchoolAI",
    #  "scraper": scrape_schoolai},
    # {"url": "https://jobs.jobvite.com/imagine-learning/jobs/viewall",
    #  "name": "Imagine Learning",
    #  "scraper": scrape_imagine_learning},
    # {"url": "https://www.edtech.com/jobs/software-engineer-jobs?ListingAge=Last%2014%20days&Country=United%20States",
    #  "name": "Edtech.com",
    #  "scraper": scrape_edtechcom},
    # {"url": "https://curriculumassociates.wd5.myworkdayjobs.com/External?jobFamilyGroup=2dd225c058cb0101b12d250db9000000&jobFamilyGroup=2dd225c058cb0101b12d2641b2550000",
    #  "name": "Curriculum Associates",
    #  "scraper": scrape_curriculumAssociates},
    # {"url": "https://greatminds.recruitee.com/?jobs-c88dea0d%5Btab%5D=all",
    #  "name": "Great Minds", 
    #  "scraper": scrape_greatMinds},
    #  {"url": "https://careers.anthology.com/search/jobs", 
    #   "name": "Blackboard/Anthology", 
    #   "scraper": scrape_anthology},
    # {"url": "https://www.prometheanworld.com/about-us/careers/", 
    #  "name": "Promethean", 
    #  "scraper": scrape_promethean},
    # {"url": "https://www.masteryprep.com/join-team/#Openings",
    #  "name": "MasteryPrep",
    #  "scraper": scrape_masteryprep},
    # {"url": "https://recruiting.ultipro.com/HOL1002HPHM/JobBoard/be27b89b-3cb9-491f-a1b0-42f8b077a9dd/?q=&o=postedDateDesc&w=&wc=&we=&wpst=&f4=P3uiKTJuwU-EMui9Ye7png&f5=Z6VUAqvr8UOWHe2Wz3tZ7w",
    #  "name": "Macmillan Learning",
    #  "scraper": scrape_macmillan},
    # {"url": "https://job-boards.greenhouse.io/newsela",
    #  "name": "Newsela",
    #  "scraper": scrape_newsela},
    # {"url": "https://jobs.dayforcehcm.com/en-US/k12l/CANDIDATEPORTAL",
    #  "name": "Savvas",
    #  "scraper": scrape_savvas},
    # {"url": "https://job-boards.greenhouse.io/edmentum",
    #  "name": "Edmentum",
    #  "scraper": scrape_edmentum},
    # {"url": "https://careers.coursera.com/jobs/search?page=1&query=&department_uids%5B%5D=0b370cc4e5d8b1fba08d06720b9850aa&country_codes%5B%5D=US",
    #  "name": "Coursera",
    #  "scraper": scrape_coursera},
    # {"url": "https://job-boards.greenhouse.io/goguardian",
    #  "name": "GoGuardian/Peardeck",
    #  "scraper": scrape_goguardian},
    # {"url": "https://careers.smartrecruiters.com/Skyward1",
    #  "name": "Skyward", 
    #  "scraper": scrape_skyward},
    # {"url": "https://pearson.jobs/locations/usa/schedule/full-time/workplace-type/remote/jobs/",
    #  "name": "Pearson",
    #  "scraper": scrape_pearson},
    # {"url": "https://www.powerschool.com/company/careers/?location=US--Remote",
    #  "name": "Powerschool",
    #  "scraper": scrape_powerschool},
    # {"url": "https://www.khanacademy.org/careers#openings", 
    #  "name": "Khan Academy",
    #  "scraper": scrape_khan},
    # {"url": "https://jobs.abre.com/",
    #  "name": "Abre",
    #  "scraper": scrape_abre},
    # {"url": "https://proxlearn.bamboohr.com/careers",
    #  "name": "Proximity Learning",
    #  "scraper": scrape_proximity_learning},
    # {"url": "https://www.governmentjobs.com/careers/colorado?location[0]=denver%20metro&department[0]=Department%20of%20Education&sort=PositionTitle%7CAscending",
    #  "name": "Colorado Dept of Ed",
    #  "scraper": scrape_coloradodoe},
    # {"url": "https://edtechjobs.io",
    #   "name": "Edtechjobs.io",
    #   "scraper": scrape_edtechjobsio},
    # {"url": "https://www.deltamath.com/jobs/",
    #  "name": "DeltaMath",
    #  "scraper": scrape_deltamath},
    # {"url": "https://jobs.cambiumlearning.com/?size=n_50_n",
    # "name": "Cambium Learning Group",
    # "scraper": scrape_cambium},
    # {"url": "https://jobs.ashbyhq.com/magicschool/",
    # "name": "Magic School",
    # "scraper": scrape_magicschool},
    # {"url": "https://www.pairin.com/about/careers/",
    #  "name": "Pairin",
    #  "scraper": scrape_pairin,
    # },
    # {"url": "https://careers.jeffco.k12.co.us/psc/careers/EMPLOYEE/APPLICANT/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?FOCUS=Applicant&SiteId=3",
    #  "name": "JeffCo Schools", 
    #  "scraper": scrape_jeffco_schools},
    # {"url": "https://dpsjobboard.dpsk12.org/en/sites/CX_1001/jobs?lastSelectedFacet=TITLES&mode=location&selectedTitlesFacet=30%3B46",
    #  "name": "Denver Public Schools",
    #  "scraper": scrape_dps_aurora},
    # {"url": "https://dcsd.wd5.myworkdayjobs.com/en-US/DCSD/details/Systems-Engineer-II_Req-00077984-2?timeType=f5213912a3b710211de745c6879eb635&jobFamily=fef6e4a613001022976a2e0edb5b3686&jobFamily=fef6e4a613001022976a2c4522c13684",
    #  "name": "DCSD",
    #  "scraper": scrape_public_schools_workday},
    # {"url": "https://fa-epop-saasfaprod1.fa.ocs.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1/jobs?lastSelectedFacet=CATEGORIES&selectedCategoriesFacet=300000024830845",
    #  "name": "Aurora Schools",
    #  "scraper": scrape_dps_aurora},
    # {"url": "https://dsstpublicschools.wd5.myworkdayjobs.com/DSST_Careers?jobFamily=a62b5af9bc7b100114066481a8960000&jobFamily=d969b57881e70103beb07a72d629da6b&jobFamily=d969b57881e70104991d7a72d629d86b",
    #  "name": "DSST System",
    #  "scraper": scrape_public_schools_workday}, 
]


chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--disable-sync")
chrome_options.add_argument("--disable-component-extensions-with-background-pages")
chrome_options.add_argument("log-level=3")
# chrome_options.add_argument("--incognito")
# chrome_options.headless = True
# chrome_options.add_argument("--window-size=1920,1200")
driver = webdriver.Chrome(options=chrome_options)

# driver = webdriver.Chrome()

all_results = {}
comprehensive_company_list = []
ordered_website_list = sorted(website_list, key=lambda x: x["name"].lower())

for site in ordered_website_list:
    print("Scraping: ", site["name"])
    comprehensive_company_list.append(site["name"])
    driver.get(site["url"])
    try:
        results = site["scraper"](driver)
        all_results[site['name']] = {
            'jobs': results if isinstance(results, list) else [results],
            'url': site['url']
        }
    except Exception as e:
        # print(f"Error with {site['name']}: {e}")
        all_results[site['name']] = {
            'jobs': [f"Error: {e}"],
            'url': site['url']
        }
        
driver.quit()

ordered_company_list = sorted(comprehensive_company_list)

# export to generated html file
results_dir = os.path.join(os.getcwd(), "front_end")
template_file = os.path.join(results_dir, "template.html")
with open(template_file, "r", encoding="utf-8") as f:
    template = f.read()

companies_list = ""
for company in ordered_company_list:
    companies_list += f'<li>{company}</li>'

company_sections = ""
for company, data in all_results.items():
    company_sections += f'<div class="company-section">\n'
    company_sections += f'  <div class="company-header"><h2 class="company-name">{company}</h2></div>\n'
    for job in data['jobs']:
        if isinstance(job, dict):
            href = job.get('href')
            info = job.get("description")
            company_sections += f'  <a href="{href}" target="_blank"><div class="job-item">{info}</div></a>\n'
        elif isinstance(job, str):
            company_sections += f'  <div class="job-item">{job}</div>\n'
        # else:
    company_sections += f'  <a href="{data["url"]}" target="_blank" class="view-link">View All Openings →</a>\n'
    company_sections += '</div>\n'

jobs_content = template.replace("{{ company_sections }}", company_sections)
jobs_content= jobs_content.replace("{{ companies_list }}", companies_list)

output_file = os.path.join(results_dir, "job_results.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(jobs_content)

webbrowser.open(f"file://{output_file}")