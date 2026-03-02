# Workout Cloning and Strava Sync Features

This update adds the ability to clone existing Hevy workouts via the command line. This is useful for pushing previous workouts to Strava, which cannot be done natively in the Hevy app for already-saved workouts.

## New CLI Tools

### 1. Manual Login Helper (`manual_login.py`)
If you are running in an environment without a GUI (like WSL2), you can use this script to log in by copying your session cookie from your Windows browser.

**How to use:**
1. Open your web browser on Windows and log in to [hevy.com](https://hevy.com).
2. Open **Developer Tools** (press **F12**).
3. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox).
4. Select **Cookies** -> `https://www.hevy.com`.
5. Find the cookie named `access-token`.
6. Copy its entire value.
7. In your terminal, run:
   ```bash
   python3 manual_login.py
   ```
8. Paste the cookie value when prompted. Your session will now be saved locally.

### 2. Workout Cloning Tool (`clone_to_strava.py`)
This script clones a local workout and submits it to Hevy with the `share_to_strava` flag set to `True`.

**How to use:**
1. First, ensure you have downloaded your latest workouts from Hevy:
   ```bash
   python3 clone_to_strava.py --sync
   ```
2. List your recent workouts and choose one to clone:
   ```bash
   python3 clone_to_strava.py --list
   ```
3. Enter the number corresponding to the workout you want to sync to Strava.

The script will create an identical copy of the workout (preserving the original timestamps) and submit it as a new workout to Hevy. Hevy's backend will then automatically push this new workout to your connected Strava account.

## Backend Changes (`hevy_api.py`)
- Added `prepare_workout_for_clone(workout_data)`: Robustly cleans workout data by removing internal IDs and mapping fields to the v2 API format.
- Added `post_workout(workout_json)`: Handles the actual submission of the cloned workout to the Hevy API.
