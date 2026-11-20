import json, os, re, sys, getpass
import requests
from bs4 import BeautifulSoup
 
HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.expanduser("~/.wilma_config.json")
SESSION = os.path.expanduser("~/.wilma_session.json")
 
 
def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
 
 
def save(path, data):
    # created as 0600 so the session cookie isn't readable by other users
    with open(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600), "w", encoding="utf-8") as f:
        json.dump(data, f)
 
 
def get_trays():
    """Return the trays page HTML, or None if we're not logged in."""
    r = s.get(f"{base}/{cfg['wilma_id']}/trays", timeout=10, allow_redirects=False)
    logged_out = (r.status_code != 200 or "login-page" in r.text
                  or "Istunnon tunniste ei kelpaa" in r.text)
    return None if logged_out else r.text
 
 
cfg = load(CONFIG)
if not cfg:
    cfg = {"login": input("Wilma login: ").strip(),
           "wilma_id": input("Wilma ID (number from URL): ").strip(),
           "base": input("Wilma URL (e.g. https://helsinki.inschool.fi): ").strip()}
    save(CONFIG, cfg)
base = cfg["base"].rstrip("/")
 
s = requests.Session()
if cached := load(SESSION):
    s.cookies.set("Wilma2SID", cached.get("Wilma2SID", ""))
 
html = get_trays()
if html is None:
    s.cookies.clear()  # drop the stale cookie so it can't mask a failed login
    pw = getpass.getpass(f"Wilma password for {cfg['login']}: ")
    sid = s.get(f"{base}/index_json", timeout=10).json()["SessionID"]
    s.post(f"{base}/login", timeout=10, allow_redirects=False,
           data={"Login": cfg["login"], "Password": pw, "SESSIONID": sid})
    if "Wilma2SID" not in s.cookies or (html := get_trays()) is None:
        sys.exit(f"login failed (delete {CONFIG} to re-enter your details)")
    save(SESSION, {"Wilma2SID": s.cookies["Wilma2SID"]})
 
table = BeautifulSoup(html, "html.parser").find("table") or sys.exit("no course table found")
code_re = re.compile(r"^([A-ZÄÖÅ]+\d+)\.")  # "MAA05.2 ..." -> "MAA05"
codes = {m[1] for row in table.find_all("tr")[1:] for td in row.find_all("td")
         if (m := code_re.match(td.get_text(" ", strip=True)))}
 
if not (credits := load(os.path.join(HERE, "tools", "courses_db.json"))):
    sys.exit("tools/courses_db.json is missing or broken, run tools/parser.py to rebuild it")
 
print(f"Found {len(codes)} courses")
for c in sorted(codes & credits.keys()):
    print(f"  + {c}: {credits[c]} ects")
print(f"\nTOTAL: {sum(credits[c] for c in codes & credits.keys())}")
if missing := sorted(codes - credits.keys()):
    print("Not in database:", missing)
