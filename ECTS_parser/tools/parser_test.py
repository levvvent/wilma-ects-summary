import requests, re, json, sys
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
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

CODE_RE = re.compile(r'^[A-ZÄÖÅ]+\d+$')
GROUP_RE = re.compile(r'/\d+/\d+$')

s = requests.Session()
sid = s.get(f"{BASE_URL}/index_json").json()["SessionID"]
s.post(f"{BASE_URL}/login", data={"Login": LOGIN, "Password": PASSWORD, "SESSIONID": sid})
if "Wilma2SID" not in s.cookies:
    sys.exit("Login failed")
print("Login successful!")

# --- 1. BFS ---
queue, seen, links = [f"{BASE_URL}/{YOUR_WILMA_ID}/catalog"], set(), set()
while queue:
    url = queue.pop()
    if url in seen: continue
    seen.add(url)
    try:
        soup = BeautifulSoup(s.get(url, timeout=10).text, "html.parser")
        for a in soup.find_all('a', href=True):
            if '/catalog/' in a['href'] and '0/0' not in a['href']:
                u = BASE_URL + a['href'] if a['href'].startswith('/') else a['href']
                if u not in seen:
                    links.add(u); queue.append(u)
    except Exception:
        pass
links = {u for u in links if not GROUP_RE.search(u)}
print(f"Links to parse: {len(links)}")

# --- 2. Parsing ---
def parse(url):
    try:
        soup = BeautifulSoup(s.get(url, timeout=10).text, "html.parser")
        credits = None
        for tr in soup.find_all('tr'):
            th, td = tr.find('th'), tr.find('td')
            if th and td and "ECTS opintopisteitä" in th.text:
                m = re.search(r'\d+[\.,]?\d*', td.text.strip())
                if m:
                    credits = float(m.group().replace(',', '.'))
                break
        if credits is None:
            return None
        for tr in soup.find_all('tr', class_='current') + soup.find_all('tr'):
            for th in tr.find_all('th'):
                if CODE_RE.match(t := th.text.strip()):
                    return t, credits
    except Exception:
        return None

with ThreadPoolExecutor(10) as ex:
    futures = {ex.submit(parse, url): url for url in links}
    db = {}
    for f in as_completed(futures):
        if r := f.result():
            db[r[0]] = r[1]
            print(f"  + {r[0]}: {r[1]} ects")

# --- 3. Saving ---
with open("../wilma_final_db.json", "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=4, sort_keys=True)
    
print(f"\nDONE! Courses collected: {len(db)}")
for p in ("ÄI", "S2", "MAA", "ENA"):
    found = sorted(c for c in db if c.startswith(p))
    print(f"  {p}: {len(found)} courses (e.g. {found[:3]}...)")