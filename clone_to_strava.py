#!/usr/bin/env python3
"""Clone to Strava

A utility script to clone an existing Hevy workout and push it to Strava.
This works by creating an identical copy of the workout with a new ID
and setting the 'share_to_strava' flag to True.
"""

import json
import os
import sys
import uuid
import random
import requests
from pathlib import Path
import hevy_api

def clone_workout(workout_file_path):
    # 1. Check if logged in to Hevy
    logged_in, user_folder, auth_token = hevy_api.is_logged_in()
    if not logged_in:
        print("Error: Not logged in to Hevy. Please run Under The Bar and log in first.")
        return False

    # 2. Load the workout JSON
    try:
        with open(workout_file_path, 'r') as f:
            workout_data = json.load(f)
    except Exception as e:
        print(f"Error loading workout file: {e}")
        return False

    # 3. Prepare the clone using the helper
    clone_data = hevy_api.prepare_workout_for_clone(workout_data)
    w = clone_data["workout"]

    # 6. Post to Hevy
    print(f"Cloning workout '{w.get('title')}' ({w.get('start_time')}) to Hevy with Strava sync...")
    
    try:
        status_code, response_text = hevy_api.post_workout(clone_data)
        
        if status_code in (200, 201):
            print("Successfully cloned workout! Hevy should now push it to your Strava account.")
            print(f"New Hevy Workout ID: {w['workout_id']}")
            return True
        else:
            print(f"Failed to clone workout. Status code: {status_code}")
            print(f"Response: {response_text}")
            return False
    except Exception as e:
        print(f"Error during API request: {e}")
        return False

def list_local_workouts():
    logged_in, user_folder, auth_token = hevy_api.is_logged_in()
    if not logged_in:
        print("Error: Not logged in to Hevy.")
        return []

    workouts_folder = Path(user_folder) / "workouts"
    if not workouts_folder.exists():
        print(f"Workouts folder not found: {workouts_folder}")
        return []

    workouts = []
    for file in sorted(os.listdir(workouts_folder), reverse=True):
        if file.endswith(".json") and file.startswith("workout_"):
            try:
                with open(workouts_folder / file, 'r') as f:
                    data = json.load(f)
                    # Handle both wrapped and unwrapped
                    w = data.get("workout", data)
                    workouts.append({
                        "filename": file,
                        "path": str(workouts_folder / file),
                        "title": w.get("title", "Untitled"),
                        "start_time": w.get("start_time", 0)
                    })
            except:
                continue
    return workouts

if __name__ == "__main__":
    import argparse
    import datetime

    parser = argparse.ArgumentParser(description="Clone a Hevy workout to push it to Strava.")
    parser.add_argument("--file", help="Path to the workout JSON file.")
    parser.add_argument("--list", action="store_true", help="List local workouts to choose from.")
    parser.add_argument("--sync", action="store_true", help="Download latest workouts from Hevy first.")

    args = parser.parse_args()

    if args.sync:
        print("Syncing workouts from Hevy...")
        status, havesome = hevy_api.batch_download()
        if status == 200:
            print("Sync complete.")
        else:
            print(f"Sync failed with status: {status}")

    if args.list:
        workouts = list_local_workouts()
        if not workouts:
            print("No local workouts found.")
            print("Try running with --sync first: python3 clone_to_strava.py --sync --list")
        else:
            print("\nRecent local workouts:")
            for i, w in enumerate(workouts[:20]):
                dt = datetime.datetime.fromtimestamp(w["start_time"])
                print(f"[{i}] {dt.strftime('%Y-%m-%d %H:%M')} - {w['title']} ({w['filename']})")
            
            choice = input("\nEnter the number of the workout to clone (or 'q' to quit): ")
            if choice.lower() != 'q':
                try:
                    idx = int(choice)
                    if 0 <= idx < len(workouts):
                        clone_workout(workouts[idx]["path"])
                    else:
                        print("Invalid selection.")
                except ValueError:
                    print("Please enter a number.")
    elif args.file:
        clone_workout(args.file)
    else:
        parser.print_help()
        print("\nExample: python3 clone_to_strava.py --list")
