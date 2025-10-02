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

excluded_terms = ["senior", "lead", "manager", "principal", "staff", "director"]

def get_wait(driver, timeout=3):
    return WebDriverWait(driver, timeout)

def jobs_list_check(jobs_list, excluded_terms=excluded_terms):
    jobs_list[:] = [
        job for job in jobs_list 
        if not any(term in job.lower() for term in excluded_terms)
    ]

def scrape_deltamath(driver):
    wait = get_wait(driver)
    roles_list_visible = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div[1]/main/div/p")))
    results = roles_list_visible.text
    return results

def scrape_cambium(driver):
    wait = get_wait(driver)
    temp_jobs_list = []
    jobs = wait.until(EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[1]/div/div/div/div[2]/div/div[1]/div/ul/li")))
    time.sleep(1)
    for job in jobs:
        title = job.text.split("\n")[0]
        location = job.text.split("\n")[1]
        temp_jobs_list.append(f"{title} - {location}")
    jobs_list_check(temp_jobs_list)
     
    return temp_jobs_list

def scrape_magicschool(driver):
    wait = get_wait(driver)
    temp_jobs_list = []
    list_of_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ashby-job-posting-brief")))
    for job in list_of_elements:
        title = job.text.split("\n")[0]
        if title == "Future Opportunities":
            break
        if "remote" in job.text.split("\n")[1].lower():
            location = "Remote"
        pay = job.text.split("\n")[2]
        temp_jobs_list.append(f"{title} - {location} - {pay}")
    jobs_list_check(temp_jobs_list)
    return temp_jobs_list


website_list = [
    {"url": "https://www.deltamath.com/jobs/",
     "name": "DeltaMath",
     "scraper": scrape_deltamath},
    {"url": "https://jobs.cambiumlearning.com/?size=n_50_n",
    "name": "Cambium Learning Group",
    "scraper": scrape_cambium},
    {"url": "https://jobs.ashbyhq.com/magicschool/",
    "name": "Magic School",
    "scraper": scrape_magicschool}
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

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Job Search Results</title>
      <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f0f2f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        header {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }}
        h1 {{
            color: #1a1a1a;
            font-size: 32px;
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
        }}
        .company-section {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .company-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .company-name {{
            font-size: 24px;
            font-weight: 600;
            color: #2563eb;
        }}
        .job-count {{
            background: #2563eb;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
        }}
        .job-item {{
            padding: 15px;
            margin: 10px 0;
            background: #f8fafc;
            border-left: 4px solid #2563eb;
            border-radius: 4px;
            transition: all 0.2s;
        }}
        .job-item:hover {{
            background: #e0f2fe;
            transform: translateX(5px);
        }}
        .view-link {{
            display: inline-block;
            margin-top: 15px;
            padding: 8px 16px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            transition: background 0.2s;
        }}
        .view-link:hover {{
            background: #1d4ed8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Job Search Results</h1>
            <p class="timestamp">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </header>
    
"""
for company, data in all_results.items():
    job_count = len(data['jobs'])

    html_content += f"""
        <div class="company-header">
            <h2 class="company-name">{company}</h2>
        </div>
"""
    for job in data['jobs']:
        html_content += f'<div class="job-item">{job}</div>\n'

    html_content += f"""
            <a href="{data['url']}" target="_blank" class="view-link">View All Openings →</a>
        </div>
"""
html_content += """
    </div>
</body>
</html>
"""

file_name = "job_results.html"
with open(file_name, "w", encoding="utf-8") as f:
    f.write(html_content)

print("results exported")
webbrowser.open(file_name)