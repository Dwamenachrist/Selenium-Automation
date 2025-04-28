# 🎬 Moviebox-SRT-and-Video-Scraper

A professional-grade automation tool built with **Selenium** to **scrape subtitles and video links** from Moviebox.ng.

Easily collect full-season subtitles, videos, or both, and automatically generate a **beautiful HTML dashboard** for downloading your media!

---

## 🚀 Features

✅ Fully automated scraping of:
- Seasons and episodes
- Subtitles (`.srt`)  
- Video files (`.mp4`) in various resolutions

✅ Dynamic detection of:
- Available seasons
- Available video resolutions (1080P, 720P, etc.)

✅ Smart scraping:
- Waits for network traffic (handles pending downloads)
- Handles all popups and overlays automatically
- Detects and captures the **final correct** subtitle and video URLs
- Retries failed downloads automatically

✅ User flexibility:
- Choose which seasons to scrape
- Choose which episodes to scrape
- Choose media type: subtitles only, videos only, or both
- Choose video resolutions (single, multiple, or all)

✅ Organized output:
- Saves links to a `.txt` file
- Generates a beautiful `.html` dashboard for easy downloads
- Generates clean filenames like `SeriesName_S01E05_720P.mp4` and `SeriesName_S01E05.srt`

✅ Logging system:
- Logs all events (success, errors, skipped episodes)
- Debugging is easy if something fails

✅ Modern code structure:
- Error handling
- WebDriver wait usage
- Clear separation of logic
- Fully scalable for large series

---

## 📸 Screenshots

| Scraping in Action | HTML Download Dashboard |
|:---:|:---:|
| ![Scraping](screenshots/scraping.gif) | ![Dashboard](screenshots/dashboard.png) |

*(Add your screenshots later!)*

---

## ⚙️ Requirements

- Python 3.8+
- Google Chrome
- Chromedriver (matching your Chrome version)
- Python packages:
  ```bash
  pip install selenium selenium-wire
