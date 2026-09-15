from src.app import create_app
import json

def debug_officer_names():
    app = create_app()
    app.config['TESTING'] = True
    
    client = app.test_client()
    
    with app.app_context():
        print("Logging in as officer1...")
        resp = client.post("/auth/login", json={"username": "officer1", "password": "password123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.json}")
            return

        token = resp.json["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("Fetching Officer Snapshot...")
        # Officer endpoint: /analytics/risk-list
        resp = client.get("/analytics/risk-list", headers=headers)
        data = resp.json
        
        if not data:
            print("No data returned.")
            return

        first = data[0]
        print(f"Sample Record: {first}")
        
        # Check for name field (mapped to username in API)
        name = first.get("username")
        if name and " " in name:
            print(f"PASS: Name '{name}' looks like a full name.")
        else:
            print(f"FAIL: Name '{name}' does not look like a full name.")

if __name__ == "__main__":
    debug_officer_names()
