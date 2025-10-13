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

# enter venv first: source env/Scripts/activate

excluded_terms = ["senior", "lead", "manager", "principal", "staff", "director", "chief", "teacher", "sr", "architect", "head", "business intelligence", "therapist", "director", "president", "sales", "counsel", "vp"]

acceptable_locations =[
        "remote" , "denver" , "co" , "colorado" , "united states" , "usa" , "us"
    ]

# General helpers---------------------------------------------
def click_element(locator, driver, time = 3):
    WebDriverWait(driver, time).until(EC.element_to_be_clickable(locator)).click()

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

def jobs_list_check(jobs_list, excluded_terms=excluded_terms):
    jobs_list[:] = [
        job for job in jobs_list 
        if not any(term in job.lower() for term in excluded_terms)
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
    jobs_list_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def jobs_aggregator_list_check(jobs_list, key, excluded_terms=excluded_terms):
    jobs_list[:] = [
        job for job in jobs_list 
        if not any(term in job[key].lower() for term in excluded_terms)
    ]
    jobs_list[:] = [
        job for job in jobs_list 
        if any(term in job[key].lower() for term in acceptable_locations)
    ]

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
        job_entry["href"] = job.get_attribute('href')
        temp_jobs_list.append(job_entry)
    jobs_aggregator_list_check(temp_jobs_list, key="description")
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    # temp_details = []
    # for job_entry in temp_jobs_list:
    #     temp_details.append(job_entry["description"])
    return temp_jobs_list

def check_location(location, title):
    if not any(term in location.lower() for term in acceptable_locations):
        return False
    if ("india") in location.lower():
        return False
    if ("telugu") in title.lower():
        return False
    return True

def scrollToBottom():
    footer_locator = (By.CSS_SELECTOR, "footer")
    wait = get_wait(driver)
    footer_element = wait.until(EC.presence_of_element_located(footer_locator))
    time.sleep(2)
    driver.execute_script("arguments[0].scrollIntoView()", footer_element)
    time.sleep(2)

# Scraper functions and niche helpers---------------------------------
def scrape_deltamath(driver):
    wait = get_wait(driver)
    roles_list_visible = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/main/div/p")))
    results = roles_list_visible.text
    return results

def scrape_cambium(driver):
    wait = get_wait(driver)
    jobs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div[1]/div/ul/li")))
    time.sleep(1)
    return parse_job_info(jobs)   

def scrape_magicschool(driver):
    wait = get_wait(driver)
    list_of_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ashby-job-posting-brief")))
    return parse_job_info(list_of_elements)

def scrape_pairin(driver):
    wait = get_wait(driver)
    element = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/section/div[6]/h4")))
    list_of_elements = driver.find_element(By.XPATH, "/html/body/div[1]/main/section/div[6]/h4")
    # NEED TO ADD SCRAPER FOR WHEN THERE IS A JOB TO TEST WITH
    return list_of_elements.text

def scrape_guild(driver):
    # client side rendering makes this not work.
    return

def scrape_dps_aurora(driver):
    wait = get_wait(driver)
    job_tiles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul span.job-tile__title")))
    return parse_job_info(job_tiles)

def scrape_public_schools_workday(driver):
    wait = get_wait(driver)
    job_listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul h3")))
    return parse_job_info(job_listings)

def parse_job_info_edtechjobsio(jobs):
    temp_jobs_list = []
    for job in jobs:
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
            temp_jobs_list.append(f"{title} - {company} - {location} - {pay} - {posted}")
    jobs_list_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def collect_multipage_edtechio(driver, url, locator, job_listings):
    wait = get_wait(driver)
    driver.get(url)
    temp_job_listings = wait.until(EC.presence_of_all_elements_located(locator))
    job_listings += parse_job_info_edtechjobsio(temp_job_listings)
    return job_listings

def scrape_edtechjobsio(driver):
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

def scrape_jeffco_schools(driver):
    locator_show_all_jobs = (By.ID, "HRS_SCH_WRK$0_row_0")
    locator_show_more_jobs = (By.XPATH, "/html/body/form/div[2]/div[4]/div[2]/div/div/div/div/div[1]/section/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[3]/fieldset/div[1]/span/a")
    locator_show_tech_jobs = (By.ID, "win0divPTS_SELECTctrl$15")
    locator_results_list = (By.XPATH, "/html/body/form/div[2]/div[4]/div[2]/div/div/div/div/div[2]/section/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div/ul/li")

    wait = get_wait(driver)
    click_element(locator_show_all_jobs, driver)
    # time.sleep(6)
    click_element(locator_show_more_jobs, driver)
    # time.sleep(6)
    click_element(locator_show_tech_jobs, driver)
    # time.sleep(6)

    jobs_list = wait.until(EC.visibility_of_all_elements_located(locator_results_list))
    return parse_job_info(jobs_list)

def scrape_coloradodoe(driver):
    locator = (By.CLASS_NAME, "job-table-title")
    wait = get_wait(driver)
    job_listings = wait.until(EC.presence_of_all_elements_located(locator))
    temp_job_list = []
    for job in job_listings:
        if "Job Title" not in job.text :         
            temp_job_list.append(job.text)
    jobs_list_check(temp_job_list)
    return temp_job_list

def scrape_proximity_learning(driver):
    locator = (By.CSS_SELECTOR, "ul li")
    wait = get_wait(driver)
    temp_jobs_list = []
    for job in wait.until(EC.presence_of_all_elements_located(locator)):
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[2] if len(lines) > 2 else ""
        if check_location(location, title) == False:
            continue
        temp_jobs_list.append(f"{title} - {location}")
    jobs_list_check(temp_jobs_list)
    return temp_jobs_list

def scrape_abre(driver):
    locator = (By.XPATH, "/html/body/main/section[2]/div[2]/div/ul/li")
    wait = get_wait(driver)
    temp_jobs_list = []
    for job in wait.until(EC.presence_of_all_elements_located(locator)):
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        temp_jobs_list.append(f"{title}")
    jobs_list_check(temp_jobs_list)
    return temp_jobs_list

def parse_khan_academy(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[1] if len(lines) > 1 else ""
        if (not check_location(location, title)) or ("talent community" in title.lower()):
            continue
        temp_jobs_list.append(f"{title} - {location}")
    jobs_list_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def scrape_khan(driver):
    locator = (By.CLASS_NAME, "_12k2rikw")
    wait = get_wait(driver)
    jobs_list =  wait.until(EC.presence_of_all_elements_located(locator))
    return parse_khan_academy(jobs_list)

def scrape_powerschool(driver):
    return "None - all tech jobs are India"

def scrape_pearson(driver):
    modal_locator = (By.ID, "onetrust-accept-btn-handler")
    # modal that is a problem to click
    return "Have to check their <a href='https://pearson.jobs/locations/usa/schedule/full-time/workplace-type/remote/jobs/' target=_blank >website</a>"

def scrape_skyward(driver):
    locator = (By.CLASS_NAME, "opening-jobs")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_job_info(jobs_list)

def parse_goguardian(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        lines = job.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[1] if len(lines) > 1 else ""
        if check_location(location, title) == False:
            continue
        temp_jobs_list.append(f"{title} - {location}")
    jobs_list_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def scrape_goguardian(driver):
    # greenhouse
    locator = (By.CSS_SELECTOR, "tbody .cell")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    jobs_texts = (job.text for job in jobs_list)
    return parse_goguardian(jobs_texts)

def scrape_coursera(driver):
    title_locator = (By.CSS_SELECTOR, ".job-search-results-title a")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(title_locator))
    temp_jobs_list = []
    for job in jobs_list:
        title = job.text.strip()
        if title:
            temp_jobs_list.append(title)
    return jobs_list_check(temp_jobs_list)

def scrape_edmentum(driver):
    return scrape_greenouse(driver)

def parse_savvas(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[1] if len(lines) > 1 else ""
        if check_location(location, title) == False:
            continue
        temp_jobs_list.append(f"{title} - {location}")
    jobs_list_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def scrape_savvas(driver):
    locator = (By.CSS_SELECTOR, ".ant-list-items li")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_savvas(jobs_list)

def scrape_newsela(driver):
    return scrape_greenouse(driver)

def parse_macmillan(jobs_list):
    temp_jobs_list = []
    for job in jobs_list:
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[5] if len(lines) > 1 else ""
        location2 = lines[10] if len(lines) > 2 else ""
        temp_jobs_list.append(f"{title} - {location} - {location2}")
    jobs_list_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("None")
    return temp_jobs_list

def scrape_macmillan(driver):
    locator = (By.CLASS_NAME, "opportunity")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_macmillan(jobs_list)

def scrape_masteryprep(driver):
    it_locator = (By.LINK_TEXT, "IT")
    jobs_locator = (By.CSS_SELECTOR, ".whr-items li")
    wait = get_wait(driver)
    wait.until(EC.element_to_be_clickable(it_locator)).click()
    time.sleep(1)
    jobs_list = wait.until(EC.presence_of_all_elements_located(jobs_locator))
    temp_jobs_list = []
    for job in jobs_list:
        # print(job.text)
        lines = job.text.split("\n")
        # print(lines)
        title, location = ""
        if len(lines) > 1:
            title = lines[0] 
            location = lines[1]
            # print(title,location)
        if len(title) != 0:
            temp_jobs_list.append(f"{title} - {location}")
    # jobs_list_check(temp_jobs_list)
    # return temp_jobs_list
    return None

def scrape_greenouse(driver):
    locator = (By.CLASS_NAME, "job-post")
    wait = get_wait(driver)
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    jobs_texts = (job.text for job in jobs_list)
    return parse_goguardian(jobs_texts)

def scrape_promethean(driver):
    # none sales and bsuiness jobs are not US based
    return None

def scrape_anthology(driver):
    return None
    # no tech jbos in US

def parse_greatMinds(jobs_list):
    temp_jobs_list = []
    row_header = "Job title Work model Location"

    for job in jobs_list:
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        if row_header not in title:
            temp_jobs_list.append(f"{title}")
    jobs_list_check(temp_jobs_list)
    if len(temp_jobs_list) == 0:
        temp_jobs_list.append("none")
    return temp_jobs_list

def scrape_greatMinds(driver):
    list_locator = (By.XPATH, "/html/body/div/div[3]/main/div[2]/section/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[2]/div/output")
    jobs_locator = (By.TAG_NAME, "tr")

    wait = get_wait(driver)
    list = wait.until(EC.presence_of_element_located(list_locator))
    jobs_list = list.find_elements(*jobs_locator)
    return parse_greatMinds(jobs_list)

def scrape_curriculumAssociates(driver):
    return "None - all tech jobs in India"

def scrape_edtechcom(driver):
    locator = (By.CSS_SELECTOR, "#listings a")
    wait = get_wait(driver)
    scrollToBottom()
    jobs_list = wait.until(EC.presence_of_all_elements_located(locator))
    return parse_aggregator_info(jobs_list)

# Todo: retry masteryprep, imaginelearning, schoolai, noredink, blackbaud, timely, turnitin, collegeboard, cengagegroup, adtalem, scholastic, adams county, mapleton
website_list = [
    {"url": "https://www.edtech.com/jobs/software-engineer-jobs?ListingAge=Last%2014%20days&Country=United%20States",
     "name": "Edtech.com",
     "scraper": scrape_edtechcom},
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
    # # NOT ACTUALLY PULLING TEXT FROM WEB ELEMENT FOR SOME REASON
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
driver = webdriver.Chrome(options=chrome_options)

# driver = webdriver.Chrome()

all_results = {}

for site in website_list:
    print("Scraping: ", site["name"])
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

# export to generated html file
results_dir = os.path.join(os.getcwd(), "results")
template_file = os.path.join(results_dir, "template.html")
with open(template_file, "r", encoding="utf-8") as f:
    template = f.read()

company_sections = ""
for company, data in all_results.items():
    company_sections += f'<div class="company-section">\n'
    company_sections += f'  <div class="company-header"><h2 class="company-name">{company}</h2></div>\n'
    for job in data['jobs']:
        if isinstance(job, dict):
            href = job.get('href')
            info = job.get("description")
            company_sections += f'  <div class="job-item"><a href="{href}" target="_blank">{info}</a></div>\n'
        elif isinstance(job, str):
            company_sections += f'  <div class="job-item">{job}</div>\n'
        # else:
    company_sections += f'  <a href="{data["url"]}" target="_blank" class="view-link">View All Openings →</a>\n'
    company_sections += '</div>\n'

html_content = template.replace("{{ timestamp }}", datetime.now().strftime("%B %d, %Y at %I:%M %p"))
html_content = html_content.replace("{{ company_sections }}", company_sections)

output_file = os.path.join(results_dir, "job_results.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open(f"file://{output_file}")