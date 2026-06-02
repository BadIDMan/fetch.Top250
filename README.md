# Kodi IMDb Top250 Fetcher
## Overview

This Python 3 script fetches the current IMDb Top250 movie ranking directly from IMDb using Playwright.<br>
It generates a lightweight dataset containing ranking positions and IMDb IDs, designed for integration with Kodi add-ons or other media management tools.<br>

The script also maintains a historical change log showing:<br>
- newly added movies<br>
- removed movies<br>
- ranking movements<br>

Movie titles and release years in the history log are resolved using The Movie Database (TMDb) API.<br>

## Problem
IMDb Top250 changes over time:<br>
- movies enter and leave the ranking<br>
- positions move daily<br>
- Kodi does not provide native Top250 synchronization<br>
- IMDb does not expose an official simple Top250 API<br>

Additionally:<br>
- IMDb page structure is JavaScript-rendered<br>
- simple requests/BeautifulSoup scraping is unreliable<br>

## Solution
This script:<br>
- Uses Playwright + Chromium to render IMDb Top250 page properly<br>
- Extracts ranking positions and IMDb IDs<br>
- Creates a minimal dataset file:<br>

rank|IMDbID<br>

Example:<br>

1|tt0111161<br>

- Detects changes between runs<br>
- Creates historical logs<br>
- Resolves movie titles and years using TMDb API<br>
- Avoids rewriting output file when no changes are detected<br>

## Output Files
### Top250.txt

Contains current IMDb Top250 dataset:<br>

1|tt0111161<br>
2|tt0068646<br>
3|tt0468569<br>

### imdb_top250_history.log
Contains historical changes:<br>

2026-05-09 10:43:22: Top250 changed!(+1 -1, moved 8)<br>
NEW: tt10431500 at #250 "Miracle in Cell No. 7 (2019)"<br>
REMOVED: tt8108198 (was #250) "Andhadhun (2018)"<br>
MOVE: tt7286456 90->89 "Joker (2019)"<br>

### Timestamped execution logs
Example:

imdb_top250_20260602075021.log

Contains:<br>
- start time<br>
- end time<br>
- number of collected IDs<br>
- execution status<br>
- Environment<br>

Designed primarily for:<br>
- Synology NAS<br>
- Linux servers<br>
- Docker environments<br>
- Kodi backend infrastructure<br>

## Important Recommendation

This script uses:<br>
- Playwright<br>
- Chromium browser binaries<br>

These dependencies are large and may introduce unnecessary complexity into Synology DSM operating system.<br>
For this reason it is strongly recommended to run the script inside Docker container instead of installing Playwright/Chromium directly into DSM.<br>

Docker provides:<br>
- isolated environment<br>
- easier dependency management<br>
- safer upgrades<br>
- cleaner DSM system<br>

## Prerequisites

Requirements:<br>
- Python 3<br>
- TMDb API key<br>
- Internet access<br>

Python modules used:<br>
- playwright<br>
- requests<br>

The script automatically installs missing Python modules if needed.<br>

## Docker Recommendation
Recommended Docker image:<br>

mcr.microsoft.com/playwright/python<br>


## Usage
1. Copy the script to your Docker mapped volume or server<br>
2. Edit CONFIG section:<br>
- output paths<br>
- TMDb API key<br>
- log retention period<br>
3. Run:<br>

python3 imdb_top250.py

## Scheduling
The script is designed for scheduled execution.<br>

Typical usage:<br>
- daily execution via Synology Task Scheduler<br>
- cron job<br>
- Docker scheduled task<br>

## Notes
The generated Top250.txt file changes only when IMDb Top250 actually changes.<br>
This allows external tools (for example Kodi add-ons) to:<br>
- compare timestamps<br>
- avoid unnecessary downloads<br>
- minimize network traffic<br>

The script is intentionally designed to store only:<br>
- ranking position<br>
- IMDb ID<br>

Movie titles are resolved dynamically only for human-readable history logs.<br>


# This project is provided for personal/private use only.

The generated dataset file:<br>

Top250.txt<br>

<b>must not be:</b><br>
- redistributed<br>
- published<br>
- mirrored<br>
- shared publicly<br>
- uploaded to websites<br>
- committed to public GitHub repositories<br>

or otherwise exposed publicly in any form.<br>

The script is intended solely to allow private synchronization of IMDb Top250 information for personal media library usage.<br>

Generating and locally using a lightweight Top250 dataset for personal/private use does not violate IMDb usage rules.<br>

However:<br>
- redistribution of IMDb-derived datasets<br>
- public mirrors<br>
- commercial usage<br>
- public APIs serving IMDb-derived data<br>

may violate IMDb Terms of Use and should be avoided.<br>

### Result in "history" log:<br>
<img width="432" height="936" alt="Screenshot_20260512_131028_SSH Remote" src="https://github.com/user-attachments/assets/cbfc4a72-ff24-4d8c-93be-9fcb39a61daa" />




