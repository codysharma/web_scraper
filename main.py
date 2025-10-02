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