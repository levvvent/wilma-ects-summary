import requests
from bs4 import BeautifulSoup
import re
import json
import sys
import os
from dotenv import load_dotenv

# ==========================================
# 1. Authorization
# ==========================================

load_dotenv()

BASE_URL = os.getenv("WILMA_BASE_URL", "https://helsinki.inschool.fi")
LOGIN = os.getenv("WILMA_LOGIN")
PASSWORD = os.getenv("WILMA_PASSWORD")
YOUR_WILMA_ID = os.getenv("WILMA_ID")

if not all([LOGIN, PASSWORD, YOUR_WILMA_ID]):
    raise SystemExit("ERROR: set WILMA_LOGIN, WILMA_PASSWORD, WILMA_ID in .env")

s = requests.Session()

print("Authorizing...")
r = s.get(f"{BASE_URL}/index_json")
sid = r.json()["SessionID"]

payload = {
    "Login": LOGIN,
    "Password": PASSWORD,
    "SESSIONID": sid,
}
r = s.post(f"{BASE_URL}/login", data=payload, allow_redirects=False)

if "Wilma2SID" not in s.cookies:
    print("ERROR: Login failed.")
    exit(1)

print("Login successful!")

# ==========================================
# 2. Parse selected courses
# ==========================================
RE = re.compile(r'^([A-ZÄÖÅ]+\d+)\.')
url = f"{BASE_URL.rstrip('/')}/{YOUR_WILMA_ID}/trays"

r = s.get(url, timeout=10)
r.raise_for_status()
assert not (r.url.endswith("/login") or "login-page" in r.text or "Istunnon tunniste ei kelpaa" in r.text), "session expired"
table = BeautifulSoup(r.text, "html.parser").find('table') or sys.exit("no table")

codes = {m[1] for row in table.find_all('tr')[1:] for c in row.find_all('td')
         if (m := RE.match(c.get_text(" ", strip=True)))}
print(f"Found: {len(codes)}", sorted(codes))

# ==========================================
# 3. Load new database
# ==========================================
with open("wilma_final_db.json", "r", encoding="utf-8") as f:
    db = json.load(f)

total = 0.0
missing = [c for c in codes if c not in db]

for c in sorted(codes - set(missing)):
    credits = db[c]
    total += credits
    print(f"  + {c}: {credits} ects")

print(f"\nTOTAL: {total}")
if missing:
    print(f"Missing codes in database: {missing}")