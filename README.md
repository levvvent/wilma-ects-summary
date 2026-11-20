# wilma-ects-summary

A small tool that counts how many credits (op / ECTS) your selected courses in Wilma add up to.

Wilma shows the courses you've picked, but not the total. This logs in as you, looks up each course's credits and adds them up.

## Setup

You need Python 3.8 or newer.

```
git clone https://github.com/levvvent/wilma-ects-summary
cd wilma-ects-summary
pip install -r requirements.txt
```

## Usage

```
cd ECTS_parser
python main.py
```

The first time, it asks for:

- your Wilma username
- your Wilma ID, which is the `!123456` part of your Wilma address
- your school's Wilma address, for example `https://helsinki.inschool.fi`
- your password

Your password is never saved. Your details and the login session are kept in `~/.wilma_config.json` and `~/.wilma_session.json`, so next time it just prints your credits.

Example output:

```
Found 24 courses
  + ENA01: 2.0 ects
  + MAA02: 3.0 ects
  ...

TOTAL: 52.0
```

## The course database

`ECTS_parser/tools/courses_db.json` already has the credits of about 570 courses from the Helsinki Wilma catalog, so you don't need to build it yourself.

If courses are missing, or your school uses a different catalog, rebuild it (log in with `main.py` first):

```
python tools/parser.py
```

## If something goes wrong

- **Login fails, or you typed something wrong:** delete `~/.wilma_config.json` and run `main.py` again.
- **parser.py says the session expired:** run `main.py` to log in again.
- **"Not in database: ...":** those courses weren't found in the catalog. Rebuild the database; if they're still missing, they may have no credits listed in Wilma.

## Note

This is an unofficial hobby project, not affiliated with Wilma or Visma. It only reads your own pages, the same as you would in a browser. Don't share `~/.wilma_session.json`: anyone who has it is logged in as you.
