from src.app import create_app
import json

def debug_restriction():
    app = create_app()
    app.config['TESTING'] = True
    
    client = app.test_client()
    
    with app.app_context():
        # 1. Login as Director 1 (CS)
        print("Logging in as director1...")
        resp = client.post("/auth/login", json={"username": "director1", "password": "password123"})
        if resp.status_code != 200:
            print(f"Login failed: {resp.json}")
            return
            
        token_cs = resp.json["token"]
        headers_cs = {"Authorization": f"Bearer {token_cs}"}
        
        # 2. Get Academic List for CS
        print("Fetching CS List...")
        resp = client.get("/analytics/academic-list", headers=headers_cs)
        cs_data = resp.json
        print(f"CS Director sees {len(cs_data)} students.")
        
        # 3. Login as Director 2 (ENG)
        print("Logging in as director2...")
        resp = client.post("/auth/login", json={"username": "director2", "password": "password123"})
        token_eng = resp.json["token"]
        headers_eng = {"Authorization": f"Bearer {token_eng}"}
        
        # 4. Get Academic List for ENG
        print("Fetching ENG List...")
        resp = client.get("/analytics/academic-list", headers=headers_eng)
        eng_data = resp.json
        print(f"ENG Director sees {len(eng_data)} students.")
        
        # 5. Verify
        cs_ids = set(d['student_id'] for d in cs_data)
        eng_ids = set(d['student_id'] for d in eng_data)
        overlap = cs_ids.intersection(eng_ids)
        
        if overlap:
            print(f"FAIL: Overlap detected! {len(overlap)} students.")
        elif len(cs_data) == 0 or len(eng_data) == 0:
            print("FAIL: No data returned.")
        else:
            print("PASS: Directors see disjoint sets of students.")
            if cs_data:
                print(f"CS Sample: {cs_data[0].get('username', 'N/A')}") # Director view might be anonymized
            if eng_data:
                print(f"ENG Sample: {eng_data[0].get('username', 'N/A')}")

if __name__ == "__main__":
    debug_restriction()
