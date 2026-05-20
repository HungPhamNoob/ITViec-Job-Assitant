import os

import cloudscraper
from bs4 import BeautifulSoup

SESSION_COOKIE = os.getenv("ITVIEC_SESSION_COOKIE", "")
TARGET_URL = "https://itviec.com/it-jobs/truong-nhom-computer-vision-ai-engineer-pytorch-vega-corporation-1049"

scraper = cloudscraper.create_scraper()

if SESSION_COOKIE:
    scraper.cookies.set("_itviec_session_v2", SESSION_COOKIE, domain="itviec.com")

response = scraper.get(TARGET_URL)
soup = BeautifulSoup(response.text, "lxml")

# Salary visibility can depend on the authenticated session cookie.
salary_tag = soup.select_one(".salary")
salary_text = salary_tag.get_text(strip=True) if salary_tag else "Salary information is not visible."
print(f"Salary: {salary_text}")
