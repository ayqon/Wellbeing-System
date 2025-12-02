from src.app import create_app
import json

def debug_full_stack():
    app = create_app()
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    
    client = app.test_client()
    
    with app.app_context():
        # 1. Login
        print("Logging in...")
        resp = client.post("/auth/login", json={
            "username": "director1",
            "password": "password123"
        })
        
        if resp.status_code != 200:
            print(f"Login Failed: {resp.status_code}")
            print(resp.json)
            return
            
        token = resp.json["token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get Risk List (Director Dashboard data)
        print("Fetching Risk List...")
        try:
            # Endpoint might be different in prototype, checking analytics routes
            # /analytics/director/dashboard returns HTML
            # /analytics/risk-list might be the API endpoint if it exists
            # Let's try /analytics/academic-list which we used in restriction debug
            resp = client.get("/analytics/academic-list", headers=headers)
            print(f"Response Status: {resp.status_code}")
            if resp.status_code == 200:
                print("Success!")
                print(str(resp.json)[:200] + "...")
            else:
                print("Failed!")
                print(resp.json)
        except Exception as e:
            print(f"Exception during request: {e}")

if __name__ == "__main__":
    debug_full_stack()
