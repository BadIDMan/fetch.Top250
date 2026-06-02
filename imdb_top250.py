import subprocess
import sys
import os
import re
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from datetime import datetime

# =========================
# CONFIG
# =========================
OUTPUT = "/data/Top250.txt" #<-- output file
TEMP_OUTPUT = "/data/Top250_temp.txt"
LOG_DIR = "/log" #<-- logs folder
LOG_FILE = "imdb_top250" #<-- log files pattern
HISTORY_LOG = "imdb_top250_history.log" #<-- file with history how rankings changes
LOG_RETENTION_DAYS = 7
TMDB_API_KEY = "11111111111111111111111111111111" #<-- put here your OWN TMDB API Key
TIME_ZONE_NAME = "Europe/Warsaw" #<-- Defines the time zone used in log files.
#The value must be a valid IANA time zone name, for example:
#Europe/Warsaw
#Europe/London
#America/New_York
#Asia/Tokyo
#Australia/Sydney
#Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIME_ZONE = ZoneInfo(TIME_ZONE_NAME)


# =========================
# PLAYWRIGHT ENSURE
# =========================
def ensure_playwright():
    try:
        import playwright
        return
    except ImportError:
        print("Playwright not found, installing...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "playwright"]
    )
    subprocess.check_call(
        [sys.executable, "-m", "playwright", "install", "chromium"]
    )

# =========================
# REQUESTS ENSURE
# =========================
def ensure_requests():
    try:
        import requests
        return
    except ImportError:
        print("Requests not found, installing...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "requests"]
    )



ensure_playwright()
ensure_requests()
from playwright.sync_api import sync_playwright
import requests

# =========================
# LOGGING
# =========================
def get_log_path():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    ts = datetime.now(TIME_ZONE).strftime("%Y%m%d%H%M%S")
    return os.path.join(
        LOG_DIR,
        f"{LOG_FILE}_{ts}.log"
    )


def cleanup_logs():
    if not os.path.exists(LOG_DIR):
        return
    cutoff = datetime.now(TIME_ZONE) - timedelta(days=LOG_RETENTION_DAYS)
    for fname in os.listdir(LOG_DIR):
        if not fname.endswith(".log"):
            continue
        # do not delete history log
        if fname == HISTORY_LOG:
            continue
        try:
            ts_str = fname.rsplit("_", 1)[1].replace(".log", "")
            file_dt = datetime.strptime(ts_str,"%Y%m%d%H%M%S")
            if file_dt < cutoff:
                os.remove(os.path.join(LOG_DIR, fname))
        except Exception as e:
            print(f"Failed to process log file "f"{fname}: {e}")


def write_log(log_path, line):
    with open(log_path, "w") as f:
        f.write(line + "\n")


# =====================================
# GET TITLE FROM TMDB USING OWN API KEY
# =====================================
def get_movie_title(imdb_id):
    url = f"https://api.themoviedb.org/3/find/{imdb_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "external_source": "imdb_id"
    }
    try:
        r = requests.get(
            url,
            params=params,
            timeout=10
        )
        if r.status_code != 200:
            return imdb_id
        data = r.json()
        movie_results = data.get("movie_results", [])
        if movie_results:
            movie = movie_results[0]
            title = movie.get("title", imdb_id)
            release_date = movie.get(
                "release_date",
                ""
            )
            year = ""
            if release_date and len(release_date) >= 4:
                year = release_date[:4]
            if year:
                return f"{title} ({year})"
            return title
        return imdb_id
    except:
        return imdb_id



# =========================
# FILE UPDATE LOGIC
# =========================
def write_if_changed(sorted_list):
    new_content = "\n".join(
        f"{rank}|{imdb_id}"
        for rank, imdb_id in sorted_list
    ) + "\n"
    # write temp file
    with open(TEMP_OUTPUT, "w") as f:
        f.write(new_content)
    # first run
    if not os.path.exists(OUTPUT):
        os.rename(TEMP_OUTPUT, OUTPUT)
        return "created"
    # compare
    with open(OUTPUT, "r") as f:
        old_content = f.read()
    if old_content == new_content:
        os.remove(TEMP_OUTPUT)
        return "unchanged"
    # replace
    os.replace(TEMP_OUTPUT, OUTPUT)
    return "updated"


# =========================
# HISTORICAL DATA
# =========================
def load_existing():
    if not os.path.exists(OUTPUT):
        return {}
    data = {}
    with open(OUTPUT, "r") as f:
        for line in f:
            rank, imdb_id = line.strip().split("|")
            data[imdb_id] = int(rank)
    return data

def compare_top250(old, new):
    changes = {
        "new": [],
        "removed": [],
        "moved": []
    }
    new_dict = {
        imdb_id: rank
        for rank, imdb_id in new
    }
    # NEW
    for imdb_id in new_dict:
        if imdb_id not in old:
            changes["new"].append(
                (imdb_id, new_dict[imdb_id])
            )
    # REMOVED
    for imdb_id in old:
        if imdb_id not in new_dict:
            changes["removed"].append(
                (imdb_id, old[imdb_id])
            )
    # MOVED
    for imdb_id in new_dict:
        if imdb_id in old:
            old_rank = old[imdb_id]
            new_rank = new_dict[imdb_id]
            if old_rank != new_rank:
                changes["moved"].append(
                    (
                        imdb_id,
                        old_rank,
                        new_rank
                    )
                )
    return changes

def append_history_detailed(status, changes, timestamp):
    history_path = os.path.join(
        LOG_DIR,
        HISTORY_LOG
    )
    lines = []
    if status == "unchanged":
        lines.append(
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}: "
            f"Top250 unchanged"
        )
    else:
        summary = (
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}: "
            f"Top250 changed! "
            f"(+{len(changes['new'])} "
            f"-{len(changes['removed'])}, "
            f"moved {len(changes['moved'])})"
        )
        lines.append(summary)
        for imdb_id, rank in changes["new"]:
            title = get_movie_title(imdb_id)
            lines.append(
                f'  NEW: {imdb_id} at #{rank} "{title}"'
            )
        for imdb_id, rank in changes["removed"]:
            title = get_movie_title(imdb_id)
            lines.append(
                f'  REMOVED: {imdb_id} '
                f'(was #{rank}) "{title}"'
            )
        for imdb_id, old, new in changes["moved"]:
            title = get_movie_title(imdb_id)
            lines.append(
                f'  MOVE: {imdb_id} '
                f'{old}->{new} "{title}"'
            )
    text = "\n".join(lines)
    with open(history_path, "a") as f:
        f.write("\n" + text + "\n")
    return text



def append_history_detailed_old(status, changes, timestamp):
    history_path = os.path.join(
        LOG_DIR,
        HISTORY_LOG
    )
    if status == "unchanged":
        line = (
            f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}: "
            f"Top250 unchanged"
        )
        with open(history_path, "a") as f:
            f.write(line + "\n")
        return
    summary = (
        f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}: "
        f"Top250 changed! "
        f"(+{len(changes['new'])} "
        f"-{len(changes['removed'])}, "
        f"moved {len(changes['moved'])})"
    )
    with open(history_path, "a") as f:
        f.write("\n" + summary + "\n")
        for imdb_id, rank in changes["new"]:
            title = get_movie_title(imdb_id)
            f.write(
                f'  NEW: {imdb_id} at #{rank} "{title}"\n'
            )
        for imdb_id, rank in changes["removed"]:
            title = get_movie_title(imdb_id)
            f.write(
                f'  REMOVED: {imdb_id} '
                f'(was #{rank}) "{title}"\n'
            )
        for imdb_id, old, new in changes["moved"]:
            title = get_movie_title(imdb_id)
            f.write(
                f'  MOVE: {imdb_id} '
                f'{old}->{new} "{title}"\n'
            )



# =========================
# MAIN
# =========================
def main():
    start_time = datetime.now(TIME_ZONE)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            viewport={
                "width": 1920,
                "height": 1080
            },
            locale="en-US"
        )
        page = context.new_page()
        page.goto(
            "https://www.imdb.com/chart/top/",
            timeout=60000
        )
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()
    results = {}
    pattern = re.findall(
        r'/title/(tt\d+)/\?ref_=chttp_[ti]_(\d+)',
        html
    )
    for imdb_id, rank in pattern:
        rank = int(rank)
        if rank not in results:
            results[rank] = imdb_id
    sorted_list = sorted(results.items())
    old_data = load_existing()
    status = write_if_changed(sorted_list)
    end_time = datetime.now(TIME_ZONE)
    if status in ("updated", "created"):
        changes = compare_top250(
            old_data,
            sorted_list
        )
    else:
        changes = None
    history_text = append_history_detailed(
        status,
        changes,
        end_time
    )
    # =========================
    # LOGGING
    # =========================
    log_path = get_log_path()

    log_header = (
        f"Start time: "
        f"{start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"End time: "
        f"{end_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Number of IDs collected: "
        f"{len(sorted_list)}\n"
        f"Status: {status}\n"
    )
    full_log = (log_header + "\n" + history_text)
    write_log(log_path, full_log)
    cleanup_logs()
    print(full_log)


if __name__ == "__main__":
    main()
