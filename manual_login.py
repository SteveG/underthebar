#!/usr/bin/env python3
import hevy_api
import getpass
import json
import urllib.parse

print("--- Hevy Manual Login Helper ---")
print("Since you are on WSL without a GUI backend, you can log in manually.")
print("\n1. Log in to https://hevy.com on your Windows browser.")
print("2. Open DevTools (F12) -> Application (or Storage) -> Cookies -> https://www.hevy.com")
print("3. Find the cookie named 'auth2.0-token'.")
print("4. Copy the entire value (it looks like %7B%22access_token%22%3A...)")

cookie_value = input("\nPaste the 'auth2.0-token' cookie value here: ").strip()

try:
    # URL decode and parse JSON
    decoded_value = urllib.parse.unquote(cookie_value)
    data = json.loads(decoded_value)
    
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    
    if not access_token or not refresh_token:
        print("Error: Could not find access_token or refresh_token in the pasted value.")
    else:
        print("\nAttempting to log in...")
        status = hevy_api.temp_login(access_token, refresh_token)
        if status == 200:
            print("\nSuccess! You are now logged in.")
            print("You can now run: python3 clone_to_strava.py --list")
        else:
            print(f"\nFailed to log in. Hevy API returned status: {status}")

except Exception as e:
    print(f"\nError parsing cookie: {e}")
    print("Make sure you copied the entire cookie value from your browser.")
