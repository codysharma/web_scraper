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

excluded_terms = ["senior", "lead", "manager", "principal", "staff", "director", "chief", "teacher", "sr", "architect", "head", "business intelligence", "therapist", "director"]

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
    return temp_jobs_list

def check_location(location):
    if ("remote" or "denver") not in location.lower():
        return False
    return True

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
    locator_show_tech_jobs = (By.ID, "PTS_FACETVALUES$1_row_11")
    locator_results_list = (By.XPATH, "/html/body/form/div[2]/div[4]/div[2]/div/div/div/div/div[2]/section/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div/ul/li")

    wait = get_wait(driver)
    click_element(locator_show_all_jobs, driver)
    click_element(locator_show_more_jobs, driver)
    click_element(locator_show_tech_jobs, driver)
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
    return temp_job_list

def scrape_proximity_learning(driver):
    locator = (By.CSS_SELECTOR, "ul li")
    wait = get_wait(driver)
    temp_jobs_list = []
    for job in wait.until(EC.presence_of_all_elements_located(locator)):
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        location = lines[2] if len(lines) > 2 else ""
        if check_location(location) == False:
            break
        temp_jobs_list.append(f"{title} - {location}")
    return temp_jobs_list

def scrape_abre(driver):
    locator = (By.XPATH, "/html/body/main/section[2]/div[2]/div/ul/li")
    wait = get_wait(driver)
    temp_jobs_list = []
    for job in wait.until(EC.presence_of_all_elements_located(locator)):
        lines = job.text.split("\n")
        title = lines[0] if len(lines) > 0 else ""
        temp_jobs_list.append(f"{title}")
    return temp_jobs_list

website_list = [
    # {"url": "https://jobs.abre.com/",
    #  "name": "Abre",
    #  "scraper": scrape_abre},
    # {"url": "https://proxlearn.bamboohr.com/careers",
    #  "name": "Proximity Learning",
    #  "scraper": scrape_proximity_learning}
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

# To add: Mastery prep, Abre, Pearson, Powerschool, Skyward, Peardeck, Coursera, Edmentum, Savvas Learning Company, Newsela, Macmillan Learning, 
]

driver = webdriver.Chrome()

all_results = {}

for site in website_list:
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
            'jobs': [f"Errof: {e}"],
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
        company_sections += f'  <div class="job-item">{job}</div>\n'
    company_sections += f'  <a href="{data["url"]}" target="_blank" class="view-link">View All Openings →</a>\n'
    company_sections += '</div>\n'

html_content = template.replace("{{ timestamp }}", datetime.now().strftime("%B %d, %Y at %I:%M %p"))
html_content = html_content.replace("{{ company_sections }}", company_sections)

output_file = os.path.join(results_dir, "job_results.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open(f"file://{output_file}")