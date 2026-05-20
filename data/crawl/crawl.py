import time

import cloudscraper
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
}


def crawl_itviec_jobs(
    max_pages=10,
    delay=1,
    output_csv=None,
    csv_header=None,
    base_url=None,
    keywords=None,
):
    scraper = cloudscraper.create_scraper()
    job_links = []
    listing_info = {}

    for keyword in keywords:
        for page in range(1, max_pages + 1):
            url = f"{base_url}/viec-lam-it/{keyword}?page={page}"
            print(f"Crawling listing page: {url}")
            response = scraper.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, "lxml")
            cards = soup.select("div.job-card")

            for card in cards:
                h3 = card.select_one("h3[data-url]")
                if not h3:
                    continue

                full_link = h3.get("data-url")
                if full_link in job_links:
                    continue

                job_links.append(full_link)
                title = h3.get_text(strip=True)

                # Company names are rendered in a secondary link within the listing card.
                company_tag = card.select_one("span.small-text a.text-rich-grey")
                company = company_tag.get_text(strip=True) if company_tag else ""

                # Location usually appears in a truncated card label.
                location_tag = card.select_one("div.text-truncate.text-nowrap")
                location = location_tag.get_text(strip=True) if location_tag else ""
                if not location:
                    for span in card.find_all("span"):
                        text = span.get_text(strip=True)
                        if text in ["Ha Noi", "Ho Chi Minh", "Da Nang", "Remote"]:
                            location = text
                            break

                # Skill tags are exposed as lightweight badge links.
                skill_tags = card.select("a.itag")
                skills = [tag.get_text(strip=True) for tag in skill_tags]

                listing_info[full_link] = {
                    "title": title,
                    "company": company,
                    "location": location,
                    "skills": ", ".join(skills),
                }

            print(f"Collected {len(job_links)} unique job links so far.")
            time.sleep(delay)

    jobs = []
    for link in job_links:
        print(f"Crawling job detail: {link}")
        job_response = scraper.get(link, headers=HEADERS, timeout=10)
        job_soup = BeautifulSoup(job_response.text, "lxml")

        for tag in job_soup.find_all(["script", "style", "nav", "noscript", "header", "footer"]):
            tag.decompose()

        info = listing_info.get(link, {})
        title = info.get("title", "")
        company = info.get("company", "")
        location = info.get("location", "")
        skills = info.get("skills", "")

        description = ""
        requirements = ""
        benefits = ""

        section = job_soup.find("section", class_="job-content")
        if section:
            for block in section.find_all("div", class_="paragraph"):
                h2 = block.find("h2")
                if not h2:
                    continue

                heading_text = h2.get_text(strip=True)
                normalized_heading = heading_text.lower()
                content = block.get_text(" ", strip=True)
                content = content.replace(heading_text, "", 1).strip()

                if "mô tả công việc" in normalized_heading or "job description" in normalized_heading:
                    description = content
                elif "yêu cầu công việc" in normalized_heading or "your skills and experience" in normalized_heading:
                    requirements = content
                elif "tại sao bạn sẽ yêu thích" in normalized_heading or "why you'll love" in normalized_heading:
                    benefits = content
                elif "lý do để gia nhập" in normalized_heading and not benefits:
                    benefits = content

        jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "skills": skills,
                "description": description,
                "requirements": requirements,
                "benefits": benefits,
                "link": link,
            }
        )
        time.sleep(delay)

    if output_csv and jobs:
        dataframe = pd.DataFrame(jobs, columns=list(csv_header.keys()))
        dataframe.to_csv(output_csv, index=False, encoding="utf-8-sig")
        print(f"Saved {len(jobs)} jobs to {output_csv}.")


if __name__ == "__main__":
    keywords = [
        "ai",
        "data-science",
        "machine-learning",
        "llm",
        "deep-learning",
        "computer-vision",
        "natural-language-processing",
        "nlp",
        "ai-research",
    ]
    base_url = "https://itviec.com"

    output_csv = "data/itviec_jobs.csv"
    csv_header = {
        "title": "",
        "company": "",
        "location": "",
        "skills": "",        # Listing skill tags.
        "description": "",   # Job description section.
        "requirements": "",  # Job requirements section from the detail page.
        "benefits": "",      # Benefits section from the detail page.
        "link": "",
    }

    max_pages = 15
    delay = 0.5

    crawl_itviec_jobs(
        max_pages=max_pages,
        delay=delay,
        output_csv=output_csv,
        csv_header=csv_header,
        base_url=base_url,
        keywords=keywords,
    )
