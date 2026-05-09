#Kodi IMDb Top250 Fetcher<br>
##Overview<br>

This Python 3 script fetches the current IMDb Top250 movie ranking directly from IMDb using Playwright.<br>
It generates a lightweight dataset containing ranking positions and IMDb IDs, designed for integration with Kodi add-ons or other media management tools.<br>

The script also maintains a historical change log showing:<br>
- newly added movies<br>
- removed movies<br>
- ranking movements<br>

Movie titles and release years in the history log are resolved using The Movie Database (TMDb) API.<br>

##Problem<br>
IMDb Top250 changes over time:<br>
- movies enter and leave the ranking<br>
- positions move daily<br>
- Kodi does not provide native Top250 synchronization<br>
- IMDb does not expose an official simple Top250 API<br>

Additionally:<br>
- IMDb page structure is JavaScript-rendered<br>
- simple requests/BeautifulSoup scraping is unreliable<br>

##Solution<br>
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

##Output Files<br>
###Top250.txt<br>

Contains current IMDb Top250 dataset:<br>

1|tt0111161
2|tt0068646
3|tt0468569

###imdb_top250_history.log<br>
Contains historical changes:<br>

2026-05-09 10:43:22: Top250 changed!(+1 -1, moved 8)<br>
NEW: tt10431500 at #250 "Miracle in Cell No. 7 (2019)"<br>
REMOVED: tt8108198 (was #250) "Andhadhun (2018)"<br>
MOVE: tt7286456 90->89 "Joker (2019)"<br>

###Timestamped execution logs<br>
Example:

20260509104322_imdb_top250.log

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

##Important Recommendation<br>

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

##Prerequisites<br>

Requirements:<br>
- Python 3<br>
- TMDb API key<br>
- Internet access<br>

Python modules used:<br>
- playwright<br>
- requests<br>

The script automatically installs missing Python modules if needed.<br>

##Docker Recommendation<br>
Recommended Docker image:<br>

mcr.microsoft.com/playwright/python<br>


##Usage<br>
1. Copy the script to your Docker mapped volume or server<br>
2. Edit CONFIG section:<br>
- output paths<br>
- TMDb API key<br>
- log retention period<br>
3. Run:<br>

python3 imdb_top250.py

##Scheduling<br>
The script is designed for scheduled execution.<br>

Typical usage:<br>
- daily execution via Synology Task Scheduler<br>
- cron job<br>
- Docker scheduled task<br>

##Notes<br>
The generated Top250.txt file changes only when IMDb Top250 actually changes.<br>
This allows external tools (for example Kodi add-ons) to:<br>
- compare timestamps<br>
- avoid unnecessary downloads<br>
- minimize network traffic<br>

The script is intentionally designed to store only:<br>
- ranking position<br>
- IMDb ID<br>

Movie titles are resolved dynamically only for human-readable history logs.<br>
