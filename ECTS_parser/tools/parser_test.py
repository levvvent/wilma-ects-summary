"""Crawl the Wilma course catalog and save {course code: credits} to courses_db.json.
Uses the login saved by main.py, so run that once first."""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "courses_db.json")
CODE_RE = re.compile(r"^[A-ZÄÖÅ]+\d+$")
GROUP_RE = re.compile(r"/\d+/\d+$")  # teaching-group pages: follow their links, but they aren't courses
WORKERS = 10


def load(path):
    try:
        with open(os.path.expanduser(path), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def expired(r):
    return (r.url.endswith("/login") or "login-page" in r.text
            or "Istunnon tunniste ei kelpaa" in r.text)


cfg, cached = load("~/.wilma_config.json"), load("~/.wilma_session.json")
if not (cfg and cached):
    sys.exit("not logged in, run main.py first")
home = f"{cfg['base'].rstrip('/')}/{cfg['wilma_id']}"
cookie = {"Wilma2SID": cached.get("Wilma2SID", "")}


def parse_course(soup):
    """Return (code, credits) if this is a course page, otherwise None."""
    credits = None
    for tr in soup.find_all("tr"):
        th, td = tr.find("th"), tr.find("td")
        if th and td and "ECTS opintopisteitä" in th.text:
            if m := re.search(r"\d+(?:[.,]\d+)?", td.text):
                credits = float(m[0].replace(",", "."))
            break
    if credits is None:
        return None
    # prefer rows marked "current"; fall back to all rows if none are marked
    for tr in (soup.find_all("tr", class_="current") or soup.find_all("tr")):
        for th in tr.find_all("th"):
            if CODE_RE.match(code := th.text.strip()):
                return code, credits
    return None


def fetch(url):
    """Download one catalog page and return (links on it, course or None)."""
    try:
        r = requests.get(url, cookies=cookie, timeout=10)
    except requests.RequestException as e:
        print(f"  ! {url}: {e}")
        return set(), None
    if expired(r):
        sys.exit("session expired, run main.py to log in again")
    soup = BeautifulSoup(r.text, "html.parser")
    links = {urljoin(url, a["href"]).split("#")[0] for a in soup.find_all("a", href=True)
             if "/catalog/" in a["href"] and not GROUP_RE.search(a["href"])}
    return links, parse_course(soup)


db, seen, todo = {}, set(), [f"{home}/catalog"]
with ThreadPoolExecutor(WORKERS) as ex:
    while todo:
        seen.update(todo)
        found = set()
        for url, (links, course) in zip(todo, ex.map(fetch, todo)):
            found |= links
            if course and not GROUP_RE.search(url) and course[0] not in db:
                db[course[0]] = course[1]
                print(f"  + {course[0]}: {course[1]} ects")
        todo = sorted(found - seen)

if not db:
    sys.exit("no courses found, keeping the old database")

with open(DB, "w", encoding="utf-8") as f:
    json.dump(db, f, ensure_ascii=False, indent=4, sort_keys=True)

print(f"\nDone! {len(db)} courses from {len(seen)} pages saved to {DB}")
for p in ("ÄI", "S2", "MAA", "ENA"):
    found = sorted(c for c in db if c.startswith(p))
    print(f"  {p}: {len(found)} courses (e.g. {found[:3]})") 
