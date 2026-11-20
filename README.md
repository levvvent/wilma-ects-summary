# wilma-ects-summary

A small tool that counts how many credits (op / ECTS) your selected courses in Wilma add up to.

Wilma shows the courses you've picked, but not the total. This logs in as you, looks up each course's credits and adds them up.

## How it works

There are two scripts:

- `parser.py` goes through the Wilma course catalog and saves every course code with its credits to `courses_db.json`. You only need to run it once, and again when the catalog changes.
- `main.py` logs you in, reads your selected courses and prints the total.

## Setup

You need Python 3.8 or newer. Install the two libraries it uses:

```
pip install requests beautifulsoup4
```

## Usage

```
python main.py     # first time: asks for your details and logs you in
python parser.py   # builds courses_db.json
python main.py     # prints your credits
```

The first time you run `main.py`, it asks for:

- your Wilma username
- your Wilma ID, which is the `!123456` part of your Wilma address
- your school's Wilma address, for example `https://helsinki.inschool.fi`
- your password

Your password is never saved. Your details and the login session are kept in `~/.wilma_config.json` and `~/.wilma_session.json`, so you don't have to log in every time.

Example output:

```
Found 24 courses
  + ENA01: 2.0 ects
  + MAA02: 3.0 ects
  ...

TOTAL: 52.0
```

## If something goes wrong

- **Login fails, or you typed something wrong:** delete `~/.wilma_config.json` and run `main.py` again.
- **parser.py says the session expired:** run `main.py` to log in again.
- **"Not in database: ...":** those courses weren't found in the catalog. Run `parser.py` again; if they're still missing, they may have no credits listed in Wilma.

## Note

This is an unofficial hobby project, not affiliated with Wilma or Visma. It only reads your own pages, the same as you would in a browser. Don't share `~/.wilma_session.json`: anyone who has it is logged in as you.
