import requests

BASE_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BASE_URL}/auth/login"
# Using academic-list as it seems to be the main data endpoint for directors
RISK_URL = f"{BASE_URL}/analytics/academic-list"

# Director Credentials (from seed.py)
USERNAME = "director1"
PASSWORD = "password123"

def debug_risk():
    print(f"Logging in as {USERNAME}...")
    try:
        resp = requests.post(LOGIN_URL, json={"username": USERNAME, "password": PASSWORD})
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} - {resp.text}")
            return
        
        token = resp.json()["token"]
        print("Login successful.")
    except Exception as e:
        print(f"Login error: {e}")
        return

    headers = {'Authorization': f'Bearer {token}'}

    print("Fetching Risk List...")
    try:
        resp = requests.get(RISK_URL, headers=headers)
        print(f"Response Status: {resp.status_code}")
        print(f"Response Text: {resp.text[:500]}...") # Truncate for readability
            
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    debug_risk()
