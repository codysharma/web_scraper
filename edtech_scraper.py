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

# enter venv first: source env/Scripts/activate

excluded_terms = ["senior", "lead", "manager", "principal", "staff", "director", "chief", "teacher", "sr", "architect"]

def get_wait(driver, timeout=3):
    return WebDriverWait(driver, timeout)

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

def scrape_deltamath(driver):
    wait = get_wait(driver)
    roles_list_visible = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/main/div/p")))
    results = roles_list_visible.text
    return results

def scrape_cambium(driver):
    wait = get_wait(driver)
    jobs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div[1]/div/ul/li")))
    time.sleep(1)
    temp_jobs_list = parse_job_info(jobs)     
    return temp_jobs_list

def scrape_magicschool(driver):
    wait = get_wait(driver)
    list_of_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ashby-job-posting-brief")))
    temp_jobs_list = parse_job_info(list_of_elements)
    return temp_jobs_list

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
    job_tiles = parse_job_info(job_tiles)
    return job_tiles

def scrape_public_schools_workday(driver):
    wait = get_wait(driver)
    job_listings = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul h3")))
    job_listings = parse_job_info(job_listings)
    return job_listings

def scrape_edtechjobsio(driver):
    wait = get_wait(driver)
    driver.get("https://edtechjobs.io/jobs/entry-level")
    job_listings = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job-listings-item")))
    job_listings = parse_job_info_edtechjobsio(job_listings)

    driver.get("https://edtechjobs.io/jobs/curriculum")
    job_listings_part2 = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "job-listings-item")))
    job_listings += parse_job_info_edtechjobsio(job_listings_part2)
    return job_listings

def scrape_jeffco_schools(driver):
    wait = get_wait(driver)
    show_all_jobs = wait.until(EC.element_to_be_clickable((By.ID, "HRS_SCH_WRK$0_row_0")))
    show_all_jobs.click()
    show_more_jobs = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/form/div[2]/div[4]/div[2]/div/div/div/div/div[1]/section/div/div/div/div[1]/div/div[1]/div[2]/div/div/div[3]/fieldset/div[1]/span/a")))
    show_more_jobs.click()
    show_tech_jobs = wait.until(EC.element_to_be_clickable((By.ID, "PTS_FACETVALUES$1_row_11")))
    show_tech_jobs.click()
    jobs_list = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "/html/body/form/div[2]/div[4]/div[2]/div/div/div/div/div[2]/section/div/div[2]/div[2]/div/div[1]/div/div[2]/div/div/div/ul/li")))
    jobs_list = parse_job_info(jobs_list)
    return jobs_list

website_list = [
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
    {"url": "https://careers.jeffco.k12.co.us/psc/careers/EMPLOYEE/APPLICANT/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?FOCUS=Applicant&SiteId=3",
     "name": "JeffCo Schools", 
     "scraper": scrape_jeffco_schools}
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

# To add: Mastery prep, CoDeptEd?, ProximityLearning, Abre, Pearson, Powerschool, Skyward, Peardeck, Coursera, Edmentum, Savvas Learning Company, Newsela, Macmillan Learning, 
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
with open("template.html", "r", encoding="utf-8") as f:
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

output_file = os.path.join(os.getcwd(), "job_results.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

webbrowser.open(f"file://{output_file}")