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
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# ─── CONFIGURATION ─────────────────────────────────────────────────────
CHROMEDRIVER_PATH = r"C:\Users\Christian\Downloads\Compressed\chromedriver-win64\chromedriver-win64\chromedriver.exe"
SERIES_URL = (
    "https://moviebox.ng/movies/weak-hero-c8debpHF2U7?id=6633755939558542480&scene=&page_from=search_detail&type=/movie/detail&utm_source=PS"
)
HEADLESS = True
MAX_RETRIES = 3
WAIT_AFTER_CLICK = 10  # Reduced to 10 seconds to grab pending URL quickly
LOG_FILE_BASE = "media_links.log"

# ─── DYNAMICALLY DETERMINE SERIES NAME ──────────────────────────────────
def extract_series_name_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/')
    parts = path.split('/')
    if len(parts) > 1 and parts[0] == 'movies':
        name_part = parts[1]
        cleaned_name = re.sub(r'-[a-zA-Z0-9]+$', '', name_part).replace('-', '_').title()
        return cleaned_name
    return "Unknown_Series"

SERIES_NAME = extract_series_name_from_url(SERIES_URL)
LOG_FILE = f"{SERIES_NAME}_{LOG_FILE_BASE}"

# ─── LOGGING SETUP ──────────────────────────────────────────────────────
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,  # DEBUG for detailed request logging
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ─── CHROME OPTIONS ─────────────────────────────────────────────────────
# Add request and response interceptors to capture video URLs

def request_interceptor(request):
    # Log or modify outgoing requests if needed
    logging.debug(f"Request URL: {request.url}")
    pass

# Update response_interceptor to accept both request and response parameters
def response_interceptor(request, response):
    # Capture video URLs from responses
    if response.headers.get('Content-Type', '').startswith('video/') or \
       any(ext in response.url.lower() for ext in ['.mp4', '.mkv', '.avi', '.m3u8']):
        logging.info(f"Captured video URL: {response.url}")
        return response.url
    return None

# Update driver setup to pass both request and response to the interceptor
def setup_driver():
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

    # Attach interceptors
    driver.response_interceptor = lambda req, res: response_interceptor(req, res)

    driver.execute_cdp_cmd("Page.setDownloadBehavior", {"behavior": "deny"})
    return driver

# ─── HANDLE POPUPS ──────────────────────────────────────────────────────
def handle_popups(driver):
    try:
        close_popup_btn = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//img[contains(@src,'data:image/png') and contains(@alt, 'moviebox close')]"))
        )
        close_popup_btn.click()
        logging.info("Closed 'Download App' popup.")
    except:
        pass

    try:
        dismiss = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//p[contains(@class,'footer-text') and normalize-space(text())=\"Don't show it today\"]"))
        )
        dismiss.click()
        logging.info("Dismissed footer popup")
    except:
        pass

# ─── WAIT FOR MASKER TO DISAPPEAR ───────────────────────────────────────
def wait_for_masker_to_disappear(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "pc-masker"))
        )
        logging.info("pc-masker overlay disappeared.")
    except:
        logging.info("No pc-masker overlay found or it didn't disappear.")
        pass

# ─── CLOSE DOWNLOAD POPUP ───────────────────────────────────────────────
def close_download_popup(driver):
    try:
        close_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'pc-close')]"))
        )
        driver.execute_script("arguments[0].click();", close_btn)
        logging.info("Closed download popup.")
        time.sleep(1)
    except:
        logging.info("No download popup close button found or already closed.")
        pass

# ─── DETECT AVAILABLE RESOLUTIONS ────────────────────────────────────────
def detect_available_resolutions():
    print("\n=== DETECTING AVAILABLE RESOLUTIONS ===")
    print("Checking first episode to determine available resolutions...")
    
    driver = setup_driver()
    available_resolutions = []
    
    try:
        driver.get(SERIES_URL)
        logging.info(f"Loaded page {SERIES_URL} to detect resolutions")
        handle_popups(driver)

        episode = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "pc-ep"))
        )
        episode.click()
        
        dl_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "pc-download-btn"))
        )
        dl_btn.click()
        
        wait_for_masker_to_disappear(driver)
        try:
            resolution_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-resolution"))
            )
            available_resolutions = [el.text for el in resolution_elements]
            print(f"Detected available resolutions: {', '.join(available_resolutions)}")
            logging.info(f"Detected available resolutions: {', '.join(available_resolutions)}")
        except:
            logging.warning("No video resolutions found. This series might only have subtitles.")
            print("No video resolutions found. This series might only have subtitles.")
            
    except Exception as e:
        logging.error(f"Error detecting resolutions: {e}")
        print(f"Error detecting resolutions: {e}")
        
    finally:
        driver.quit()
        
    return available_resolutions

# ─── USER PREFERENCES ────────────────────────────────────────────────────
def get_media_preferences(available_resolutions):
    print("\n=== MEDIA TYPE SELECTION ===")
    print("What type of media would you like to download?")
    print("1. Subtitles only")
    print("2. Videos only")
    print("3. Both subtitles and videos")
    
    while True:
        choice = input("Enter your choice (1-3): ").strip()
        if choice in ['1', '2', '3']:
            break
        print("Invalid choice. Please enter 1, 2, or 3.")
    
    download_subtitles = choice in ['1', '3']
    download_videos = choice in ['2', '3']
    
    selected_resolutions = []
    if download_videos:
        if not available_resolutions:
            print("\nNo video resolutions were detected. You may only be able to download subtitles.")
            download_videos = False
        else:
            print("\n=== VIDEO RESOLUTION SELECTION ===")
            print(f"Available resolutions: {', '.join(available_resolutions)}")
            print("Which resolutions would you like to download?")
            print("1. All available resolutions")
            print("2. Highest available resolution only")
            print("3. Custom selection")
            
            while True:
                res_choice = input("Enter your choice (1-3): ").strip()
                if res_choice in ['1', '2', '3']:
                    break
                print("Invalid choice. Please enter 1, 2, or 3.")
            
            if res_choice == '1':
                selected_resolutions = available_resolutions
            elif res_choice == '2':
                resolution_priority = ["1080P", "720P", "480P", "360P", "240P"]
                for res in resolution_priority:
                    if res in available_resolutions:
                        selected_resolutions = [res]
                        break
                if not selected_resolutions and available_resolutions:
                    selected_resolutions = [available_resolutions[0]]
            else:
                print(f"Enter the resolutions you want (comma-separated, e.g., {', '.join(available_resolutions[:2])} ):")
                custom_res = input().strip().upper()
                selected_resolutions = [r.strip() for r in custom_res.split(',')]
                selected_resolutions = [r for r in selected_resolutions if r in available_resolutions]
                if not selected_resolutions:
                    print("No valid resolutions selected. Defaulting to highest available.")
                    for res in resolution_priority:
                        if res in available_resolutions:
                            selected_resolutions = [res]
                            break
                    if not selected_resolutions and available_resolutions:
                        selected_resolutions = [available_resolutions[0]]
    
    return {
        'download_subtitles': download_subtitles,
        'download_videos': download_videos,
        'selected_resolutions': selected_resolutions
    }

# ─── MAIN EXECUTION ─────────────────────────────────────────────────────
available_resolutions = detect_available_resolutions()
user_prefs = get_media_preferences(available_resolutions)

# ─── SET OUTPUT FILES BASED ON PREFERENCES ─────────────────────────────────
if user_prefs['download_subtitles'] and user_prefs['download_videos']:
    OUTPUT_TXT = f"{SERIES_NAME}_media_links.txt"
    OUTPUT_HTML = f"{SERIES_NAME}_download_media.html"
elif user_prefs['download_subtitles']:
    OUTPUT_TXT = f"{SERIES_NAME}_subtitle_links.txt"
    OUTPUT_HTML = f"{SERIES_NAME}_download_subtitles.html"
else:
    OUTPUT_TXT = f"{SERIES_NAME}_video_links.txt"
    OUTPUT_HTML = f"{SERIES_NAME}_download_videos.html"

# ─── LOAD EXISTING LINKS ────────────────────────────────────────────────
existing_eps = set()
if os.path.exists(OUTPUT_TXT):
    with open(OUTPUT_TXT, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|', 1)
            if len(parts) == 2:
                ep_str, _ = parts
                if '(' in ep_str and ')' in ep_str:
                    existing_eps.add(ep_str)
                else:
                    try:
                        existing_eps.add(int(ep_str))
                    except ValueError:
                        pass

# ─── SCRAPING LOGIC ─────────────────────────────────────────────────────
media_map = {}
driver = setup_driver()

try:
    driver.get(SERIES_URL)
    logging.info(f"Loaded page {SERIES_URL}")
    handle_popups(driver)

    season_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-se"))
    )
    seasons = [(i+1, el) for i, el in enumerate(season_elements)]

    if not seasons:
        print("No seasons found.")
        driver.quit()
        exit()

    print(f"Found {len(seasons)} seasons.")
    print("Available Seasons:", ', '.join([f"S{num:02d}" for num, _ in seasons]))

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

        season_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-se"))
        )
        current_season_btn = season_elements[season_num - 1]
        driver.execute_script("arguments[0].scrollIntoView(true);", current_season_btn)
        driver.execute_script("arguments[0].click();", current_season_btn)
        print(f"\n🔵 Processing Season {season_num:02d}...\n")
        time.sleep(2)

        episodes = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-ep"))
        )
        total_eps = len(episodes)
        print(f"Found {total_eps} episodes in Season {season_num:02d}.")

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
            handle_popups(driver)
            ep_num = idx + 1
            ep_key_base = (season_num, ep_num)
            ep_key_str_base = f"({season_num}, {ep_num})"
            
            if ep_key_str_base in existing_eps:
                print(f"Season {season_num:02d} Episode {ep_num:02d} already processed; skipping.")
                continue

            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    eps = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-ep"))
                    )
                    ep = eps[idx]
                    driver.execute_script("arguments[0].scrollIntoView(true);", ep)
                    ep.click()

                    dl_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "pc-download-btn"))
                    )
                    dl_btn.click()
                    wait_for_masker_to_disappear(driver)

                    if user_prefs['download_subtitles']:
                        try:
                            eng_btn = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'pc-select-sub') and text()='English']"))
                            )
                            driver.requests.clear()
                            eng_btn.click()
                            time.sleep(WAIT_AFTER_CLICK)
                            subtitle_links = [
                                r.url for r in driver.requests
                                if r.url and (
                                    (".srt" in r.url.lower() and '/subtitle/' in r.url.lower()) or
                                    (".vtt" in r.url.lower())
                                )
                            ]
                            if subtitle_links:
                                final_subtitle = subtitle_links[-1]
                                subtitle_key = (*ep_key_base, 'subtitle', 'default')
                                media_map[subtitle_key] = final_subtitle
                                print(f"Season {season_num:02d} Episode {ep_num:02d}: Captured subtitle → {final_subtitle}")
                                logging.info(f"Season {season_num:02d} Episode {ep_num:02d}: Subtitle → {final_subtitle}")
                            else:
                                print(f"Season {season_num:02d} Episode {ep_num:02d}: Subtitle URL not found")
                                logging.warning(f"Season {season_num:02d} Episode {ep_num:02d}: No subtitle URL captured")
                        except Exception as e:
                            logging.error(f"Error processing subtitle for S{season_num:02d}E{ep_num:02d}: {e}")
                            print(f"Error processing subtitle: {e}")

                    if user_prefs['download_videos']:
                        try:
                            resolution_elements = WebDriverWait(driver, 5).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-resolution"))
                            )
                            episode_resolutions = [el.text for el in resolution_elements]
                        except:
                            episode_resolutions = []
                            print(f"Season {season_num:02d} Episode {ep_num:02d}: No resolutions available")
                            logging.warning(f"No resolutions available for S{season_num:02d}E{ep_num:02d}")

                        for resolution in user_prefs['selected_resolutions']:
                            if resolution not in episode_resolutions:
                                print(f"Resolution {resolution} not available for Season {season_num:02d} Episode {ep_num:02d}")
                                logging.warning(f"Resolution {resolution} not found for S{season_num:02d}E{ep_num:02d}")
                                continue

                            # Update video scraping logic to use the simpler approach
                            mp4_links = [r.url for r in driver.requests if ".mp4" in r.url.lower()]

                            if mp4_links:
                                final_video = mp4_links[-1]
                                video_key = (*ep_key_base, 'video', resolution.lower())
                                media_map[video_key] = final_video
                                print(f"Season {season_num:02d} Episode {ep_num:02d}: Captured {resolution} video → {final_video}")
                                logging.info(f"Season {season_num:02d} Episode {ep_num:02d}: {resolution} video → {final_video}")
                            else:
                                print(f"Season {season_num:02d} Episode {ep_num:02d}: {resolution} video URL not found")
                                logging.warning(f"Season {season_num:02d} Episode {ep_num:02d}: No {resolution} video URL captured")

                    close_download_popup(driver)
                    driver.get(SERIES_URL)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-ep"))
                    )
                    season_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-se"))
                    )
                    new_season_btn = season_elements[season_num - 1]
                    driver.execute_script("arguments[0].click();", new_season_btn)
                    time.sleep(2)
                    break
                except (TimeoutException, NoSuchElementException, ElementClickInterceptedException) as e:
                    if attempt == MAX_RETRIES:
                        print(f"Season {season_num:02d} Episode {ep_num:02d} skipped after {MAX_RETRIES} retries: {e}")
                        logging.error(f"Failed Season {season_num:02d} Episode {ep_num:02d}: {e}")
                    else:
                        print(f"Attempt {attempt} failed, retrying...")
                        close_download_popup(driver)
                        time.sleep(2)

finally:
    driver.quit()

# ─── WRITE LINKS TO FILE ────────────────────────────────────────────────
existing_links = {}
if os.path.exists(OUTPUT_TXT):
    with open(OUTPUT_TXT, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|', 2)
            if len(parts) >= 2:
                key_str, url = parts[0], parts[1]
                if key_str.startswith('(') and key_str.endswith(')'):
                    key_parts = key_str.strip('()').split(',')
                    if len(key_parts) >= 4:
                        season = int(key_parts[0])
                        episode = int(key_parts[1])
                        media_type = key_parts[2].strip().strip("'\"")
                        resolution = key_parts[3].strip().strip("'\"")
                        existing_links[(season, episode, media_type, resolution)] = url
                    elif len(key_parts) == 2:
                        season = int(key_parts[0])
                        episode = int(key_parts[1])
                        existing_links[(season, episode, 'subtitle', 'default')] = url

all_links = {**existing_links, **media_map}

with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
    for key in sorted(all_links.keys()):
        url = all_links[key]
        f.write(f"{str(key)}|{url}\n")

print(f"Saved links for {len(all_links)} media items to {OUTPUT_TXT}")

# ─── DETERMINE FILE EXTENSION BASED ON MEDIA TYPE ─────────────────────────
def get_file_extension(url, media_type):
    url_lower = url.lower()
    if media_type == 'subtitle':
        if '.srt' in url_lower:
            return '.srt'
        elif '.vtt' in url_lower:
            return '.vtt'
        return '.srt'
    elif media_type == 'video':
        if '.mp4' in url_lower:
            return '.mp4'
        elif '.mkv' in url_lower:
            return '.mkv'
        elif '.avi' in url_lower:
            return '.avi'
        elif '.m3u8' in url_lower:
            return '.m3u8'
        return '.mp4'
    return '.txt'

# ─── GENERATE EPISODE DATA FOR HTML ─────────────────────────────────────
episodes_data = []
for key, url in sorted(all_links.items()):
    if len(key) != 4:
        print(f"Skipping invalid key format: {key}")
        continue
    season, episode, media_type, resolution = key
    file_ext = get_file_extension(url, media_type)
    if media_type == 'video' and resolution != 'default':
        fname = f"{SERIES_NAME}_S{season:02d}E{episode:02d}_{resolution}{file_ext}"
    else:
        fname = f"{SERIES_NAME}_S{season:02d}E{episode:02d}{file_ext}"
    episodes_data.append({
        "season": season,
        "episode": episode,
        "url": url,
        "fname": fname,
        "mediaType": media_type,
        "resolution": resolution if resolution != 'default' else None
    })

episodes_json = json.dumps(episodes_data, indent=2)

# ─── GENERATE HTML FILE ─────────────────────────────────────────────────
if not os.path.exists("template.html"):
    print(f"Warning: HTML template file 'template.html' not found. Please create it first.")
else:
    with open("template.html", 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = html_content.replace('{SERIES_NAME}', SERIES_NAME)
    html_content = html_content.replace('{EPISODE_COUNT}', str(len(episodes_data)))
    html_content = html_content.replace('{EPISODES_JSON}', episodes_json)
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Generated {OUTPUT_HTML} with {len(episodes_data)} media items across {len(set((ep['season'], ep['episode']) for ep in episodes_data))} episodes")
    print(f"Open {OUTPUT_HTML} in your browser to download media files")