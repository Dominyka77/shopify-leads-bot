import os
import requests
import re
import time
import pandas as pd
from bs4 import BeautifulSoup

# Load your SerpApi key from environment variable
from dotenv import load_dotenv
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Email extractor

def extract_email(text):
    matches = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}", text)
    for email in matches:
        if not any(x in email.lower() for x in ["noreply", "no-reply", "donotreply", ".png", ".jpg", ".css"]):
            return email
    return "No Email Found"

# Scrape email and Instagram from a store

def scrape_store_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        paths = ["/", "/contact", "/about", "/pages/contact", "/pages/about"]

        title = "No Title"
        email = "No Email Found"
        insta = "No Instagram Found"

        for i, path in enumerate(paths):
            try:
                response = requests.get(url.rstrip('/') + path, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, "html.parser")

                if i == 0 and soup.title:
                    title = soup.title.string.strip()

                mailto_links = [a['href'] for a in soup.find_all('a', href=True) if 'mailto:' in a['href']]
                if mailto_links:
                    email = mailto_links[0].replace("mailto:", "")
                    break

                found_email = extract_email(response.text)
                if found_email != "No Email Found":
                    email = found_email

                if insta == "No Instagram Found":
                    links = [a['href'] for a in soup.find_all('a', href=True)]
                    insta_links = [link for link in links if 'instagram.com' in link]
                    if insta_links:
                        insta = insta_links[0]
            except:
                continue

        return {
            "store_name": title,
            "url": url,
            "email": email,
            "instagram": insta
        }
    except Exception as e:
        return {"error": str(e), "url": url}

# Use SerpApi to find Shopify stores based on user keywords

def find_shopify_urls_serpapi(keywords, limit=100):
    urls = []
    for keyword in keywords:
        for start in range(0, limit, 10):
            params = {
                "engine": "google",
                "q": f"site:myshopify.com inurl:products {keyword}",
                "api_key": SERPAPI_KEY,
                "start": start
            }
            response = requests.get("https://serpapi.com/search", params=params)
            data = response.json()
            if "organic_results" not in data:
                break
            for result in data["organic_results"]:
                link = result.get("link")
                if link and link not in urls:
                    urls.append(link)
            time.sleep(1)
    return urls

# Main function to run the scraper with given keywords

def run_scraper(keywords):
    if not SERPAPI_KEY:
        raise ValueError("SerpApi API key is not set in the environment variables.")

    print(f"🔍 Finding Shopify stores for: {keywords}")
    shopify_urls = find_shopify_urls_serpapi(keywords, limit=100)
    print(f"✅ Found {len(shopify_urls)} stores")

    results = []
    for url in shopify_urls:
        data = scrape_store_data(url)
        results.append(data)

    filename = "shopify_leads_results.csv"
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)
    print(f"✅ Scraping complete. Saved to {filename}")
    return filename
