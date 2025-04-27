import os
import time
import logging
import json
from urllib.parse import urlparse
import re
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ─── CONFIGURATION ─────────────────────────────────────────────────────
CHROMEDRIVER_PATH = r"C:\Users\Christian\Downloads\Compressed\chromedriver-win64\chromedriver-win64\chromedriver.exe"
SERIES_URL = (
  "https://moviebox.ng/movies/are-you-safe-4OK7DTTtA43?id=2580011989393099376&scene=&page_from=search_detail&type=/movie/detail"
)
HEADLESS = True
MAX_RETRIES = 3
WAIT_AFTER_CLICK = 5  # seconds
LOG_FILE_BASE = "srt_links.log"

# ─── DYNAMICALLY DETERMINE SERIES NAME ──────────────────────────────────
def extract_series_name_from_url(url):
    """Extracts a simplified series name from the MovieBox URL."""
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/')
    parts = path.split('/')
    if len(parts) > 1 and parts[0] == 'movies':
        # Extract the name part (e.g., 'you-il6E41WZWa9')
        name_part = parts[1]
        # Remove the unique identifier and clean up the name
        cleaned_name = re.sub(r'-[a-zA-Z0-9]+$', '', name_part).replace('-', '_').title()
        return cleaned_name
    return "Unknown_Series"

SERIES_NAME = extract_series_name_from_url(SERIES_URL)
OUTPUT_TXT = f"{SERIES_NAME}_srt_links.txt"
OUTPUT_HTML = f"{SERIES_NAME}_download_srt.html"
LOG_FILE = f"{SERIES_NAME}_{LOG_FILE_BASE}"

# ─── LOGGING SETUP ──────────────────────────────────────────────────────
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ─── LOAD EXISTING LINKS ────────────────────────────────────────────────
existing_eps = set()
if os.path.exists(OUTPUT_TXT):
    with open(OUTPUT_TXT, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|', 1)
            if len(parts) == 2:
                ep_str, _ = parts
                # Try to parse as tuple first (for season, episode format)
                if '(' in ep_str and ')' in ep_str:
                    existing_eps.add(ep_str)
                else:
                    # Legacy format - just episode number
                    try:
                        existing_eps.add(int(ep_str))
                    except ValueError:
                        pass

# ─── CHROME OPTIONS ─────────────────────────────────────────────────────
chrome_opts = Options()
prefs = {
    "download_restrictions": 3,
    "download.prompt_for_download": False,
    "profile.default_content_settings.popups": 0
}
chrome_opts.add_experimental_option("prefs", prefs)
if HEADLESS:
    chrome_opts.add_argument("--headless=new")
chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_argument("--window-size=1920,1080")
chrome_opts.add_experimental_option("detach", True)

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_opts)
driver.execute_cdp_cmd("Page.setDownloadBehavior", {"behavior": "deny"})

# ─── SCRAPING LOGIC ─────────────────────────────────────────────────────
srt_map = {}  # (season_number, episode_number) -> srt_url mapping

try:
    driver.get(SERIES_URL)
    logging.info(f"Loaded page {SERIES_URL}")

    # Close "Download App" popup if it appears
    try:
        close_popup_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//img[contains(@src,'data:image/png') and contains(@alt, 'moviebox close')]"))
        )
        close_popup_btn.click()
        logging.info("Closed 'Download App' popup.")
        print("Closed 'Download App' popup.")
    except:
        logging.info("No 'Download App' popup found.")

    # Dismiss "Don't show it today" popup if it appears
    try:
        dismiss = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//p[contains(@class,'footer-text') and normalize-space(text())=\"Don't show it today\"]"))
        )
        dismiss.click()
        logging.info("Dismissed footer popup")
        print("Dismissed popup.")
    except:
        pass

    # Find all available seasons
    season_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-se"))
    )
    seasons = [(i+1, el) for i, el in enumerate(season_elements)]  # (season_number, element)

    if not seasons:
        print("No seasons found.")
        driver.quit()
        exit()

    print(f"Found {len(seasons)} seasons.")
    print("Available Seasons:", ', '.join([f"S{num:02d}" for num, _ in seasons]))

    # Ask which seasons to scrape
    raw = input("Enter season numbers to scrape (e.g. 1-3 or 1,3,5), ENTER for all: ").strip()
    selected_seasons = set()
    if not raw:
        selected_seasons = {num for num, _ in seasons}
    else:
        parts = raw.split(',')
        for part in parts:
            if '-' in part:
                a, b = map(int, part.split('-'))
                selected_seasons.update(range(a, b+1))
            else:
                selected_seasons.add(int(part))

    selected_seasons = sorted(selected_seasons)
    print(f"Selected seasons: {selected_seasons}\n")

    for season_num, season_btn in seasons:
        if season_num not in selected_seasons:
            continue

        # 🔥 REFRESH season buttons
        season_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-se"))
        )
        current_season_btn = season_elements[season_num - 1]
    
        # Click the fresh season button
        driver.execute_script("arguments[0].scrollIntoView(true);", current_season_btn)
        driver.execute_script("arguments[0].click();", current_season_btn)
        print(f"\n🔵 Processing Season {season_num:02d}...\n")
        time.sleep(2)  # Wait for episodes to refresh

        # Get episodes after switching season
        episodes = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-ep"))
        )
        total_eps = len(episodes)
        print(f"Found {total_eps} episodes in Season {season_num:02d}.")

        # Ask for episode range
        raw = input(f"Enter episode range for S{season_num:02d} (e.g. 5-7) or ENTER for all: ").strip()
        if not raw:
            start, end = 1, total_eps
        elif '-' in raw:
            a, b = map(int, raw.split('-'))
            start, end = a, b
        else:
            start, end = int(raw), total_eps

        start = max(1, min(start, total_eps))
        end = max(start, min(end, total_eps))
        print(f"Scraping episodes {start}–{end}...\n")

        for idx in range(start - 1, end):
            ep_num = idx + 1
            ep_key = (season_num, ep_num)
            ep_key_str = f"({season_num}, {ep_num})"
            
            if ep_key_str in existing_eps or ep_key in srt_map:
                print(f"Season {season_num:02d} Episode {ep_num:02d} already processed; skipping.")
                continue

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    eps = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-ep"))
                    )
                    ep = eps[idx]
                    driver.requests.clear()

                    driver.execute_script("arguments[0].scrollIntoView(true);", ep)
                    ep.click()

                    # Click download button
                    dl_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "pc-download-btn"))
                    )
                    dl_btn.click()

                    # Click "English" subtitle button
                    eng_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'pc-select-sub') and text()='English']"))
                    )
                    eng_btn.click()

                    # Wait for network traffic
                    time.sleep(WAIT_AFTER_CLICK)

                    # Capture only valid .srt links (no msubt)
                    srt_links = [
                        r.url for r in driver.requests
                        if ".srt" in r.url.lower() and '/subtitle/' in r.url.lower()
                    ]

                    if srt_links:
                        final_srt = srt_links[-1]
                        srt_map[ep_key] = final_srt
                        print(f"Season {season_num:02d} Episode {ep_num:02d}: Captured → {final_srt}")
                        logging.info(f"Season {season_num:02d} Episode {ep_num:02d}: {final_srt}")
                    else:
                        print(f"Season {season_num:02d} Episode {ep_num:02d}: .srt URL not found")
                        logging.warning(f"Season {season_num:02d} Episode {ep_num:02d}: No .srt URL captured")

                    # Return to main page (if needed)
                    driver.get(SERIES_URL)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-ep"))
                    )
                    # Switch back to correct season again
                    season_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-se"))
                    )
                    new_season_btn = season_elements[season_num - 1]
                    driver.execute_script("arguments[0].click();", new_season_btn)
                    time.sleep(2)

                    break

                except Exception as e:
                    if attempt == MAX_RETRIES:
                        print(f"Season {season_num:02d} Episode {ep_num:02d} skipped after {MAX_RETRIES} retries.")
                        logging.error(f"Failed Season {season_num:02d} Episode {ep_num:02d}: {e}")

finally:
    driver.quit()


# ─── WRITE LINKS TO FILE ────────────────────────────────────────────────
existing_links = {}
if os.path.exists(OUTPUT_TXT):
    with open(OUTPUT_TXT, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|', 1)
            if len(parts) == 2:
                key_str, url = parts
                # Try to parse as tuple
                if '(' in key_str and ')' in key_str:
                    try:
                        # Format is like "(1, 2)" for season 1, episode 2
                        key_str = key_str.strip('()')
                        season, episode = map(int, key_str.split(','))
                        existing_links[(season, episode)] = url
                    except ValueError:
                        pass
                else:
                    # Legacy format - just episode number, assume season 1
                    try:
                        episode = int(key_str)
                        existing_links[(1, episode)] = url
                    except ValueError:
                        pass

# Merge existing links with new ones
all_links = {**existing_links, **srt_map}

# Write back to file with tuple format
with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
    for key in sorted(all_links.keys()):
        url = all_links[key]
        f.write(f"({key[0]}, {key[1]})|{url}\n")

print(f"Saved links for {len(all_links)} episodes to {OUTPUT_TXT}")

# ─── GENERATE EPISODE DATA FOR HTML ─────────────────────────────────────
# Create a list of episode data for the HTML template
episodes_data = []
for key, url in sorted(all_links.items()):
    if not isinstance(key, tuple) or len(key) != 2:
        print(f"Skipping invalid key format: {key}")
        continue

    season, episode = key
    fname = f"{SERIES_NAME}_S{season:02d}E{episode:02d}.srt"
    episodes_data.append({
        "season": season,
        "episode": episode,
        "url": url,
        "fname": fname
    })

# Convert to JSON for the template
episodes_json = json.dumps(episodes_data, indent=2)

# ─── GENERATE HTML FILE ─────────────────────────────────────────────────
# Check if the HTML template exists
if not os.path.exists("template.html"):
    print(f"Warning: HTML template file 'template.html' not found. Please create it first.")
    print("You can use the provided HTML template and save it as this file.")
else:
    # Read the HTML template
    with open("template.html", 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace placeholders
    html_content = html_content.replace('{SERIES_NAME}', SERIES_NAME)
    html_content = html_content.replace('{EPISODE_COUNT}', str(len(episodes_data)))
    html_content = html_content.replace('{EPISODES_JSON}', episodes_json)
    
    # Write the updated HTML file
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated {OUTPUT_HTML} with {len(episodes_data)} episodes across {len(set(ep['season'] for ep in episodes_data))} seasons")
    print(f"Open {OUTPUT_HTML} in your browser to download subtitles")