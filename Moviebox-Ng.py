#########################    Working Version 1 but dowloads and saves links  #########################

# This script scrapes subtitle links from the Moviebox website using Selenium.
# It allows the user to specify a range of episodes to scrape and logs the results.
# It also handles popups and retries failed attempts to find subtitle links.
# The script uses Selenium Wire to capture network requests and extract subtitle links.
# It saves the extracted links to a text file for later use.
# The script is designed to be run in a Python environment with the necessary libraries installed.

########################################################################################################

# from seleniumwire import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# import time
# import logging

# # Setup logging
# logging.basicConfig(filename="srt_links.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# # Output file
# OUTPUT_FILE = "srt_links.txt"

# # Chrome options
# chrome_options = Options()
# # chrome_options.add_argument("--headless")  # Optional: uncomment if you want full background mode
# chrome_options.add_experimental_option("detach", True)

# # Set chromedriver path
# service = Service(r"C:\Users\Christian\Downloads\Compressed\chromedriver-win64\chromedriver-win64\chromedriver.exe")
# driver = webdriver.Chrome(service=service, options=chrome_options)

# # Series page
# series_url = "https://moviebox.ng/movies/dashing-youth-2XVAuLnCMy2?id=2149475170648506320&scene=&page_from=search_detail&type=/movie/detail"

# # Initialize
# srt_links = []

# try:
#     driver.get(series_url)
#     logging.info(f"Loaded series page: {series_url}")

#     # Handle popup ("Don't show it today")
#     try:
#         dont_show_btn = WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), \"Don't show it today\")]"))
#         )
#         dont_show_btn.click()
#         logging.info("Dismissed popup.")
#         time.sleep(1)
#     except Exception:
#         logging.info("No popup found.")

#     # Wait for episodes
#     episode_container = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "pc-ep-contain"))
#     )
#     episode_divs = episode_container.find_elements(By.CLASS_NAME, "pc-ep")

#     total_eps = len(episode_divs)
#     print(f"Found {total_eps} episodes.")

#     # Ask user where to start and end
#     user_range = input(f"Enter episode range (e.g. 5-7), single start (e.g. 3), or ENTER for all: ").strip()
#     if "-" in user_range:
#         start_ep, end_ep = map(int, user_range.split("-"))
#     elif user_range.isdigit():
#         start_ep = end_ep = int(user_range)
#     else:
#         start_ep = 1
#         end_ep = total_eps

#     print(f"→ Scraping episodes {start_ep} through {end_ep}\n")

#     # Loop episodes
#     for index in range(start_ep - 1, end_ep):
#         success = False
#         for attempt in range(3):
#             try:
#                 # Refresh episode list each time
#                 episode_container = WebDriverWait(driver, 10).until(
#                     EC.presence_of_element_located((By.CLASS_NAME, "pc-ep-contain"))
#                 )
#                 episode_divs = episode_container.find_elements(By.CLASS_NAME, "pc-ep")
#                 ep_div = episode_divs[index]

#                 # Clear old requests
#                 driver.requests.clear()

#                 # Click episode
#                 driver.execute_script("arguments[0].scrollIntoView(true);", ep_div)
#                 ep_div.click()

#                 # Wait download button
#                 download_btn = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.CLASS_NAME, "pc-download-btn"))
#                 )
#                 download_btn.click()

#                 # Wait subtitle language option
#                 subtitle_btn = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'pc-select-sub') and text()='English']"))
#                 )
#                 subtitle_btn.click()

#                 # Wait for the browser to load requests
#                 time.sleep(3)

#                 # Scan network traffic for .srt files
#                 found = False
#                 for request in driver.requests:
#                     if request.response and ".srt" in request.url:
#                         srt_links.append(request.url)
#                         print(f"Episode {index + 1}: Found SRT → {request.url}")
#                         logging.info(f"Episode {index + 1}: Found SRT → {request.url}")
#                         found = True
#                         break

#                 if not found:
#                     print(f"Episode {index + 1}: No SRT found after clicking.")
#                     logging.warning(f"Episode {index + 1}: No SRT found after clicking.")

#                 success = True
#                 break

#             except Exception as e:
#                 print(f"Episode {index + 1}: attempt {attempt + 1} failed — {e}")
#                 logging.error(f"Episode {index + 1}: attempt {attempt + 1} failed — {e}")
#                 driver.get(series_url)
#                 time.sleep(2)

#         if not success:
#             print(f"Episode {index + 1}: skipped after 3 attempts.")
#             logging.warning(f"Episode {index + 1}: skipped after 3 attempts.")

# finally:
#     driver.quit()

#     # Save collected SRT links
#     with open(OUTPUT_FILE, "w") as f:
#         for link in srt_links:
#             f.write(link + "\n")

#     print(f"\nDone! Extracted {len(srt_links)} link(s) → {OUTPUT_FILE}")
#     logging.info(f"Extracted {len(srt_links)} SRT links.")


#########################    Working Version 1 but saves only srt links and creates an html file to easily dowload all at once  #########################

# This script scrapes subtitle links from the Moviebox website using Selenium.
# It allows the user to specify a range of episodes to scrape and logs the results.
# It also handles popups and retries failed attempts to find subtitle links.
# The script uses Selenium Wire to capture network requests and extract subtitle links.
# It saves the extracted links to a text file for later use.
# The script is designed to be run in a Python environment with the necessary libraries installed.

###########################################################################################################################################################

# import os
# import time
# import logging
# from seleniumwire import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# # ─── CONFIGURATION ─────────────────────────────────────────────────────
# CHROMEDRIVER_PATH = r"C:\Users\Christian\Downloads\Compressed\chromedriver-win64\chromedriver-win64\chromedriver.exe"
# SERIES_URL = (
#     "https://moviebox.ng/movies/dashing-youth-2XVAuLnCMy2"
#     "?id=2149475170648506320&scene=&page_from=search_detail&type=/movie/detail"
# )
# SERIES_NAME = "Dashing_Youth"
# HEADLESS = False
# MAX_RETRIES = 3
# WAIT_AFTER_CLICK = 5  # seconds
# OUTPUT_TXT = f"{SERIES_NAME}_srt_links.txt"
# OUTPUT_HTML = f"{SERIES_NAME}_download_srt.html"
# LOG_FILE = f"{SERIES_NAME}_srt_links.log"

# # ─── LOGGING SETUP ──────────────────────────────────────────────────────
# logging.basicConfig(
#     filename=LOG_FILE,
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

# # ─── LOAD EXISTING LINKS ────────────────────────────────────────────────
# existing_eps = set()
# if os.path.exists(OUTPUT_TXT):
#     with open(OUTPUT_TXT, 'r', encoding='utf-8') as f:
#         for line in f:
#             ep_str, _ = line.strip().split('|', 1)
#             existing_eps.add(int(ep_str))

# # ─── CHROME OPTIONS ─────────────────────────────────────────────────────
# chrome_opts = Options()
# prefs = {
#     "download_restrictions": 3,
#     "download.prompt_for_download": False,
#     "profile.default_content_settings.popups": 0
# }
# chrome_opts.add_experimental_option("prefs", prefs)
# if HEADLESS:
#     chrome_opts.add_argument("--headless=new")
# chrome_opts.add_argument("--disable-gpu")
# chrome_opts.add_argument("--window-size=1920,1080")
# chrome_opts.add_experimental_option("detach", True)

# service = Service(CHROMEDRIVER_PATH)
# driver = webdriver.Chrome(service=service, options=chrome_opts)
# driver.execute_cdp_cmd("Page.setDownloadBehavior", {"behavior": "deny"})

# # ─── SCRAPING LOGIC ─────────────────────────────────────────────────────
# srt_map = {}  # episode_number -> srt_url mapping
# try:
#     driver.get(SERIES_URL)
#     logging.info(f"Loaded page {SERIES_URL}")

#     # Dismiss "Don't show it today" popup if it appears
#     try:
#         dismiss = WebDriverWait(driver, 5).until(
#             EC.element_to_be_clickable((By.XPATH, "//p[contains(@class,'footer-text') and normalize-space(text())=\"Don't show it today\"]"))
#         )
#         dismiss.click()
#         logging.info("Dismissed footer popup")
#         print("Dismissed popup.")
#     except:
#         pass

#     # Get all episode cards
#     episodes = WebDriverWait(driver, 10).until(
#         EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-ep"))
#     )
#     total_eps = len(episodes)
#     print(f"Found {total_eps} episodes.")

#     # Ask for range
#     raw = input("Enter range (e.g. 5-7), single start (e.g. 3), or ENTER for all: ").strip()
#     if not raw:
#         start, end = 1, total_eps
#     elif '-' in raw:
#         a, b = raw.split('-', 1)
#         start, end = int(a), int(b)
#     else:
#         start, end = int(raw), total_eps

#     start = max(1, min(start, total_eps))
#     end = max(start, min(end, total_eps))
#     print(f"Scraping episodes {start}–{end}...\n")

#     for idx in range(start - 1, end):
#         ep_num = idx + 1
#         if ep_num in existing_eps:
#             print(f"Episode {ep_num} already processed; skipping.")
#             continue

#         for attempt in range(1, MAX_RETRIES + 1):
#             try:
#                 eps = WebDriverWait(driver, 10).until(
#                     EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-ep"))
#                 )
#                 ep = eps[idx]
#                 driver.requests.clear()

#                 driver.execute_script("arguments[0].scrollIntoView(true);", ep)
#                 ep.click()

#                 dl_btn = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.CLASS_NAME, "pc-download-btn"))
#                 )
#                 dl_btn.click()

#                 eng_btn = WebDriverWait(driver, 10).until(
#                     EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'pc-select-sub') and text()='English']"))
#                 )
#                 eng_btn.click()

#                 # Wait to allow network traffic to fully load
#                 time.sleep(WAIT_AFTER_CLICK)

#                 # Collect only valid subtitle links (not msubt)
#                 srt_links = [
#                     r.url for r in driver.requests
#                     if ".srt" in r.url.lower() and '/subtitle/' in r.url.lower()
#                 ]

#                 if srt_links:
#                     final_srt = srt_links[-1]
#                     srt_map[ep_num] = final_srt
#                     print(f"Episode {ep_num}: Captured → {final_srt}")
#                     logging.info(f"Episode {ep_num}: {final_srt}")
#                 else:
#                     print(f"Episode {ep_num}: .srt URL not found")
#                     logging.warning(f"Episode {ep_num}: No .srt URL captured")

#                 # Return to main page
#                 driver.get(SERIES_URL)
#                 WebDriverWait(driver, 10).until(
#                     EC.presence_of_all_elements_located((By.CLASS_NAME, "pc-ep"))
#                 )
#                 break
#             except Exception as e:
#                 if attempt == MAX_RETRIES:
#                     print(f"Episode {ep_num} skipped after {MAX_RETRIES} retries.")
#                     logging.error(f"Failed episode {ep_num}: {e}")

# finally:
#     driver.quit()

# # ─── WRITE LINKS TO FILE ────────────────────────────────────────────────
# existing_links = {}
# if os.path.exists(OUTPUT_TXT):
#     with open(OUTPUT_TXT, 'r', encoding='utf-8') as f:
#         for line in f:
#             ep_str, url = line.strip().split('|', 1)
#             existing_links[int(ep_str)] = url

# all_links = {**existing_links, **srt_map}

# with open(OUTPUT_TXT, 'w', encoding='utf-8') as f:
#     for ep in sorted(all_links):
#         f.write(f"{ep}|{all_links[ep]}\n")

# print(f"Saved links for {len(all_links)} episodes to {OUTPUT_TXT}")

# # Generate episode list items
# items = ''
# for ep in sorted(all_links):
#     url = all_links[ep]
#     fname = f"{SERIES_NAME}_Episode_{ep:02d}.srt"
#     items += f'            <li><input type="checkbox" class="epCb" id="ep{ep}" value="{url}" data-fname="{fname}"><label for="ep{ep}"> Episode {ep}: {fname}</label></li>\n'

# # Generate enhanced HTML with cinema-inspired UI
# html = f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#   <meta charset="UTF-8">
#   <meta name="viewport" content="width=device-width, initial-scale=1.0">
#   <title>Download {SERIES_NAME} Subtitles</title>
#   <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap">
#   <style>
#     :root {{
#       --primary: #e50914;
#       --primary-hover: #f40612;
#       --secondary: #032541;
#       --text: #333;
#       --text-light: #eee;
#       --bg-light: #f8f9fa;
#       --bg-dark: #141414;
#       --card-light: #ffffff;
#       --card-dark: #1f1f1f;
#       --border-light: #e6e6e6;
#       --border-dark: #333;
#       --success: #01b4e4;
#       --downloaded: rgba(1, 180, 228, 0.15);
#       --shadow-light: 0 8px 30px rgba(0, 0, 0, 0.12);
#       --shadow-dark: 0 8px 30px rgba(0, 0, 0, 0.3);
#       --transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
#     }}

#     * {{
#       margin: 0;
#       padding: 0;
#       box-sizing: border-box;
#     }}

#     body {{
#       font-family: 'Montserrat', sans-serif;
#       background-color: var(--bg-light);
#       color: var(--text);
#       margin: 0;
#       padding: 0;
#       min-height: 100vh;
#       transition: var(--transition);
#     }}

#     .app-container {{
#       display: flex;
#       flex-direction: column;
#       min-height: 100vh;
#     }}

#     header {{
#       background-color: var(--secondary);
#       color: white;
#       padding: 1rem;
#       text-align: center;
#       box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
#     }}

#     .logo {{
#       font-size: 1.8rem;
#       font-weight: 700;
#       margin: 0;
#       display: flex;
#       align-items: center;
#       justify-content: center;
#     }}

#     .logo span {{
#       color: var(--primary);
#     }}

#     .logo-icon {{
#       margin-right: 10px;
#       font-size: 2rem;
#     }}

#     main {{
#       flex: 1;
#       display: flex;
#       justify-content: center;
#       align-items: center;
#       padding: 2rem 1rem;
#     }}

#     .container {{
#       width: 100%;
#       max-width: 650px;
#       background: var(--card-light);
#       padding: 2rem;
#       border-radius: 16px;
#       box-shadow: var(--shadow-light);
#       transition: var(--transition);
#     }}

#     h1 {{
#       margin-bottom: 1.5rem;
#       font-weight: 600;
#       font-size: 1.8rem;
#       text-align: center;
#     }}

#     .search-container {{
#       display: flex;
#       gap: 10px;
#       margin-bottom: 1.5rem;
#     }}

#     input[type=text] {{
#       flex: 1;
#       padding: 12px 16px;
#       border: 2px solid var(--border-light);
#       border-radius: 8px;
#       font-size: 1rem;
#       transition: var(--transition);
#       font-family: inherit;
#     }}

#     input[type=text]:focus {{
#       outline: none;
#       border-color: var(--primary);
#       box-shadow: 0 0 0 3px rgba(229, 9, 20, 0.2);
#     }}

#     button {{
#       padding: 12px 20px;
#       border: none;
#       background-color: var(--primary);
#       color: white;
#       font-size: 1rem;
#       font-weight: 600;
#       border-radius: 8px;
#       cursor: pointer;
#       transition: var(--transition);
#       font-family: inherit;
#       display: inline-flex;
#       align-items: center;
#       justify-content: center;
#     }}

#     button:hover {{
#       background-color: var(--primary-hover);
#       transform: translateY(-2px);
#     }}

#     button:active {{
#       transform: translateY(0);
#     }}

#     .episode-list-container {{
#       margin: 1.5rem 0;
#       border-radius: 12px;
#       border: 2px solid var(--border-light);
#       overflow: hidden;
#       transition: var(--transition);
#     }}

#     .episode-list-header {{
#       background-color: var(--secondary);
#       color: white;
#       padding: 12px 16px;
#       font-weight: 600;
#       display: flex;
#       justify-content: space-between;
#     }}

#     .selection-controls {{
#       display: flex;
#       gap: 10px;
#       margin-top: 10px;
#     }}

#     .selection-controls button {{
#       padding: 8px 12px;
#       font-size: 0.85rem;
#       background-color: var(--secondary);
#     }}

#     ul {{
#       list-style: none;
#       padding: 0;
#       margin: 0;
#       max-height: 350px;
#       overflow-y: auto;
#       scrollbar-width: thin;
#       scrollbar-color: var(--primary) var(--bg-light);
#     }}

#     ul::-webkit-scrollbar {{
#       width: 8px;
#     }}

#     ul::-webkit-scrollbar-track {{
#       background: var(--bg-light);
#     }}

#     ul::-webkit-scrollbar-thumb {{
#       background-color: var(--primary);
#       border-radius: 20px;
#     }}

#     li {{
#       padding: 16px;
#       border-bottom: 1px solid var(--border-light);
#       cursor: pointer;
#       transition: var(--transition);
#       display: flex;
#       align-items: center;
#     }}

#     li:last-child {{
#       border-bottom: none;
#     }}

#     li:hover {{
#       background-color: rgba(229, 9, 20, 0.05);
#     }}

#     li.downloaded {{
#       background-color: var(--downloaded);
#     }}

#     li input[type="checkbox"] {{
#       margin-right: 12px;
#       width: 18px;
#       height: 18px;
#       accent-color: var(--primary);
#     }}

#     .actions {{
#       display: flex;
#       justify-content: space-between;
#       align-items: center;
#       margin-top: 1.5rem;
#     }}

#     .download-btn {{
#       background: var(--primary);
#       display: flex;
#       align-items: center;
#       gap: 8px;
#       padding: 12px 24px;
#     }}

#     .toggle-btn {{
#       background: var(--secondary);
#       display: flex;
#       align-items: center;
#       gap: 8px;
#     }}

#     .toggle-btn:hover {{
#       background: #043b63;
#     }}

#     .progress {{
#       margin-top: 1rem;
#       font-size: 0.9rem;
#       color: var(--text);
#       text-align: center;
#       height: 24px;
#       transition: var(--transition);
#     }}

#     .progress-bar {{
#       height: 6px;
#       width: 100%;
#       background-color: var(--border-light);
#       border-radius: 3px;
#       margin-top: 8px;
#       overflow: hidden;
#       display: none;
#     }}

#     .progress-bar-fill {{
#       height: 100%;
#       background-color: var(--primary);
#       width: 0%;
#       transition: width 0.3s ease;
#     }}

#     .toast {{
#       position: fixed;
#       bottom: 20px;
#       right: 20px;
#       background: var(--success);
#       color: white;
#       padding: 12px 20px;
#       border-radius: 8px;
#       box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
#       transform: translateY(100px);
#       opacity: 0;
#       transition: all 0.3s ease;
#       z-index: 1000;
#       display: flex;
#       align-items: center;
#       gap: 10px;
#     }}

#     .toast.show {{
#       transform: translateY(0);
#       opacity: 1;
#     }}

#     .selected-count {{
#       background: var(--secondary);
#       color: white;
#       padding: 4px 8px;
#       border-radius: 12px;
#       font-size: 0.8rem;
#       margin-left: 8px;
#     }}

#     /* Dark mode styles */
#     body.dark {{
#       background-color: var(--bg-dark);
#       color: var(--text-light);
#     }}

#     body.dark .container {{
#       background-color: var(--card-dark);
#       box-shadow: var(--shadow-dark);
#     }}

#     body.dark input[type=text] {{
#       background-color: #2b2b2b;
#       border-color: var(--border-dark);
#       color: var(--text-light);
#     }}

#     body.dark .episode-list-container {{
#       border-color: var(--border-dark);
#     }}

#     body.dark li {{
#       border-color: var(--border-dark);
#     }}

#     body.dark li:hover {{
#       background-color: rgba(229, 9, 20, 0.15);
#     }}

#     body.dark .progress-bar {{
#       background-color: #333;
#     }}

#     /* Animation keyframes */
#     @keyframes pulse {{
#       0% {{ transform: scale(1); }}
#       50% {{ transform: scale(1.05); }}
#       100% {{ transform: scale(1); }}
#     }}

#     @keyframes fadeIn {{
#       from {{ opacity: 0; }}
#       to {{ opacity: 1; }}
#     }}

#     /* Responsive styles */
#     @media (max-width: 768px) {{
#       .container {{
#         padding: 1.5rem;
#       }}

#       .search-container {{
#         flex-direction: column;
#       }}

#       button {{
#         width: 100%;
#       }}

#       .actions {{
#         flex-direction: column;
#         gap: 1rem;
#       }}

#       .toggle-btn, .download-btn {{
#         width: 100%;
#       }}
#     }}
#   </style>
# </head>
# <body>
#   <div class="app-container">
#     <header>
#       <h1 class="logo">
#         <span class="logo-icon">🎬</span>
#         <span>{SERIES_NAME}</span><span>Subtitles</span>
#       </h1>
#     </header>

#     <main>
#       <div class="container">
#         <h1>Download {SERIES_NAME} Subtitles</h1>
        
#         <div class="search-container">
#           <input type="text" id="searchInput" placeholder="Search episodes...">
#         </div>
        
#         <div class="selection-controls">
#           <button onclick="selectAll()">Select All</button>
#           <button onclick="deselectAll()">Deselect All</button>
#           <span id="selectedCount" class="selected-count">0 selected</span>
#         </div>
        
#         <div class="episode-list-container">
#           <div class="episode-list-header">
#             <span>Available Episodes</span>
#             <span id="episodeCount">{len(all_links)} Episodes</span>
#           </div>
#           <ul id="episodeList">
# {items}
#           </ul>
#         </div>
        
#         <div class="progress">
#           <span id="progressText"></span>
#           <div class="progress-bar" id="progressBar">
#             <div class="progress-bar-fill" id="progressBarFill"></div>
#           </div>
#         </div>
        
#         <div class="actions">
#           <button class="download-btn" onclick="downloadSelected()">
#             <span>⬇️</span>
#             <span>Download Selected</span>
#           </button>
          
#           <button class="toggle-btn" onclick="toggleDarkMode()">
#             <span id="themeIcon">🌙</span>
#             <span id="themeText">Dark Mode</span>
#           </button>
#         </div>
#       </div>
#     </main>

#     <div class="toast" id="toast">
#       <span>✅</span>
#       <span id="toastMessage"></span>
#     </div>
#   </div>

#   <script>
#     // Check for saved theme preference
#     if (localStorage.getItem('darkMode') === 'true') {{
#       document.body.classList.add('dark');
#       document.getElementById('themeIcon').textContent = '☀️';
#       document.getElementById('themeText').textContent = 'Light Mode';
#     }}

#     // Track selected count
#     function updateSelectedCount() {{
#       const count = document.querySelectorAll('#episodeList input[type="checkbox"]:checked').length;
#       const countElement = document.getElementById('selectedCount');
#       countElement.textContent = count === 1 ? '1 selected' : `${{count}} selected`;
#     }}

#     // Add event listeners to all checkboxes
#     document.querySelectorAll('#episodeList input[type="checkbox"]').forEach(checkbox => {{
#       checkbox.addEventListener('change', updateSelectedCount);
#     }});

#     // Select all episodes
#     function selectAll() {{
#       const checkboxes = document.querySelectorAll('#episodeList input[type="checkbox"]');
#       checkboxes.forEach(checkbox => {{
#         checkbox.checked = true;
#       }});
#       updateSelectedCount();
#       showToast('All episodes selected');
#     }}

#     // Deselect all episodes
#     function deselectAll() {{
#       const checkboxes = document.querySelectorAll('#episodeList input[type="checkbox"]');
#       checkboxes.forEach(checkbox => {{
#         checkbox.checked = false;
#       }});
#       updateSelectedCount();
#       showToast('All episodes deselected');
#     }}

#     // Search functionality
#     document.getElementById('searchInput').addEventListener('input', function() {{
#       const searchTerm = this.value.toLowerCase();
#       const items = document.querySelectorAll('#episodeList li');
      
#       items.forEach(item => {{
#         const text = item.textContent.toLowerCase();
#         if (text.includes(searchTerm)) {{
#           item.style.display = '';
#         }} else {{
#           item.style.display = 'none';
#         }}
#       }});
#     }});

#     // Show toast notification
#     function showToast(message, duration = 3000) {{
#       const toast = document.getElementById('toast');
#       const toastMessage = document.getElementById('toastMessage');
      
#       toastMessage.textContent = message;
#       toast.classList.add('show');
      
#       setTimeout(() => {{
#         toast.classList.remove('show');
#       }}, duration);
#     }}

#     // Toggle dark/light mode
#     function toggleDarkMode() {{
#       const isDarkMode = document.body.classList.toggle('dark');
#       localStorage.setItem('darkMode', isDarkMode);
      
#       const themeIcon = document.getElementById('themeIcon');
#       const themeText = document.getElementById('themeText');
      
#       themeIcon.textContent = isDarkMode ? '☀️' : '🌙';
#       themeText.textContent = isDarkMode ? 'Light Mode' : 'Dark Mode';
      
#       // Add fade-in animation to the container
#       const container = document.querySelector('.container');
#       container.style.animation = 'fadeIn 0.5s';
#       setTimeout(() => {{ container.style.animation = ''; }}, 500);
#     }}

#     // Download selected subtitles
#     async function downloadSelected() {{
#       const selected = document.querySelectorAll('#episodeList input[type="checkbox"]:checked');
      
#       if (selected.length === 0) {{
#         showToast('Please select at least one episode', 3000);
#         return;
#       }}
      
#       const progressText = document.getElementById('progressText');
#       const progressBar = document.getElementById('progressBar');
#       const progressBarFill = document.getElementById('progressBarFill');
      
#       progressText.textContent = `Preparing to download ${{selected.length}} episodes...`;
#       progressBar.style.display = 'block';
#       progressBarFill.style.width = '0%';
      
#       let successCount = 0;
#       let failCount = 0;
      
#       for (let i = 0; i < selected.length; i++) {{
#         const checkbox = selected[i];
#         const listItem = checkbox.closest('li');
#         const url = checkbox.value;
#         const fname = checkbox.dataset.fname;
        
#         try {{
#           // Update progress
#           progressText.textContent = `Downloading ${{i + 1}}/${{selected.length}}: ${{fname}}`;
#           progressBarFill.style.width = `${{{((i + 1) / selected.length) * 100}}}%`;
          
#           // Add visual pulse effect
#           listItem.style.animation = 'pulse 0.5s';
          
#           // Fetch and download the subtitle file
#           const res = await fetch(url);
#           if (!res.ok) throw new Error(`HTTP error! status: ${{res.status}}`);
          
#           const blob = await res.blob();
#           const a = document.createElement('a');
#           a.href = URL.createObjectURL(blob);
#           a.download = fname;
#           a.click();
          
#           // Mark as downloaded
#           listItem.classList.add('downloaded');
#           successCount++;
          
#           // Small delay between downloads
#           await new Promise(r => setTimeout(r, 500));
#         }} catch (error) {{
#           console.error(`Error downloading ${{fname}}:`, error);
#           failCount++;
#         }} finally {{
#           // Reset animation
#           setTimeout(() => {{ listItem.style.animation = ''; }}, 500);
#         }}
#       }}
      
#       // Show completion message
#       if (failCount === 0) {{
#         progressText.textContent = `✅ Successfully downloaded ${{successCount}} episodes!`;
#         showToast(`Downloaded ${{successCount}} episodes successfully!`, 4000);
#       }} else {{
#         progressText.textContent = `✅ Downloaded ${{successCount}} episodes, ❌ Failed: ${{failCount}}`;
#         showToast(`Downloaded ${{successCount}} episodes, ${{failCount}} failed`, 4000);
#       }}

#       // Hide progress bar after a delay
#       setTimeout(() => {{
#         progressBar.style.display = 'none';
#       }}, 5000);
#     }}

#     // Add fade-in animation on page load
#     document.addEventListener('DOMContentLoaded', () => {{
#       document.querySelector('.container').style.animation = 'fadeIn 0.8s';
#       updateSelectedCount();
#     }});
#   </script>
# </body>
# </html>
# """

# with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
#     f.write(html)

# print(f"Generated {OUTPUT_HTML}")
