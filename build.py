#!/usr/bin/env python3
"""Regenerate every figure and every project card on the profile from live
GitHub data.

Run locally with a token that can read public data:

    GITHUB_TOKEN=$(gh auth token) python build.py

In CI the workflow passes the job's GITHUB_TOKEN. Note the query asks for
user(login:...) and not viewer — inside Actions `viewer` is the bot, not the profile owner.

Each figure is written twice, once per theme, and the README pairs them in a
<picture> so a reader on either GitHub theme gets the one meant for them.
"""

import html as html_lib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import assets                                            # noqa: E402
from theme import THEMES                                 # noqa: E402

USER = "Burak-ML"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "assets")
README = os.path.join(ROOT, "README.md")

QUERY = """
query($login: String!) {
  user(login: $login) {
    login createdAt
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC,
                 orderBy: {field: CREATED_AT, direction: ASC}) {
      totalCount
      nodes {
        name createdAt pushedAt stargazerCount isFork isArchived
        description
        licenseInfo { spdxId }
        repositoryTopics(first: 6) { nodes { topic { name } } }
        primaryLanguage { name }
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
  }
}
"""



def fetch_public_contributions(year):
    """Read the same public contribution calendar GitHub renders on the profile.

    Unlike the repository-scoped Actions token, this HTML includes anonymized
    private contribution counts when the profile owner has chosen to publicize
    them. That makes the generated heatmap match the graph a visitor sees.
    """
    url = (
        "https://github.com/users/%s/contributions?from=%d-01-01&to=%d-12-31"
        % (USER, year, year)
    )
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER + "-profile-builder",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", "replace")

    tooltip_counts = {}
    for m in re.finditer(
        r'<tool-tip\b[^>]*for="([^"]+)"[^>]*>(.*?)</tool-tip>',
        body,
        flags=re.S,
    ):
        text = html_lib.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        cm = re.search(r"([\d,]+)\s+contributions?", text)
        tooltip_counts[m.group(1)] = int(cm.group(1).replace(",", "")) if cm else 0

    days = {}
    for m in re.finditer(r"<td\b[^>]*ContributionCalendar-day[^>]*>", body):
        tag = m.group(0)
        dm = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', tag)
        lm = re.search(r'data-level="([0-4])"', tag)
        im = re.search(r'id="([^"]+)"', tag)
        if not dm or not lm:
            continue
        days[dm.group(1)] = {
            "count": tooltip_counts.get(im.group(1), 0) if im else 0,
            "level": int(lm.group(1)),
        }

    if not days:
        raise RuntimeError("GitHub contribution HTML returned no day cells")
    return days

def fetch():
    token = (os.environ.get("PROFILE_TOKEN") or os.environ.get("GITHUB_TOKEN")
             or os.environ.get("GH_TOKEN"))
    if not token:
        sys.exit("GITHUB_TOKEN is not set. Try: GITHUB_TOKEN=$(gh auth token) python scripts/build.py")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": "bearer " + token,
                 "Content-Type": "application/json",
                 "User-Agent": USER + "-profile-builder"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit("GraphQL error: " + json.dumps(payload["errors"])[:400])
    user = payload["data"]["user"]
    # A personal PROFILE_TOKEN can see private contribution data,
    # so keep the GraphQL data in that case. With the repository-scoped Actions
    # token, fall back to GitHub's public profile HTML so the visible public graph
    # and its activity levels still match GitHub exactly.
    if not os.environ.get("PROFILE_TOKEN"):
        try:
            year = datetime.utcnow().year
            user["_profileCalendar"] = fetch_public_contributions(year)
            print("profile calendar: %d public-view days for %d" %
                  (len(user["_profileCalendar"]), year))
        except Exception as e:
            print("WARNING: public contribution calendar scrape failed: %s" % e)
    return user


# --------------------------------------------------------------------------- project cards

# Prose worth keeping, written by hand, for the projects that have a real
# description in them. Anything NOT in here still gets a card — built from the
# repo's own GitHub description — so a new repository shows up on the profile
# without anyone editing this file. The two kinds of card are deliberately
# identical in chrome: a reader should not be able to tell which ones the author
# could not be bothered to write about.
CURATED = {
    "RoveCode_plugins": (
        ["TypeScript", "MCP", "AI Automation"],
        "An MCP-based skill and memory system that routes AI coding requests "
        "to relevant tools, with documented evaluation scripts."
    ),
    "Rove_cli": (
        ["Wails", "React", "TypeScript"],
        "A local-first coding agent with a shared daemon and desktop interface "
        "for sessions, terminal workflows and automations."
    ),
    "ModelAudit": (
        ["LLM Evaluation", "Research", "AI"],
        "An exploratory framework for comparing LLM behavior and documenting "
        "model attribution hypotheses; not a definitive identity test."
    ),
    "SearchForge_open": (
        ["Python", "FastAPI", "Next.js", "Google Drive"],
        "A document search and PDF reading application connecting Google Drive "
        "with a Python backend, keyword search and caching."
    ),
    "fast_f1_data": (
        ["Python", "SQL", "PostgreSQL", "FastAPI"],
        "A Formula 1 data analysis app using SQL queries, a Python API and "
        "interactive driver, team and lap comparisons."
    ),
    "KeyLingo": (
        ["Python", "macOS", "DeepL API"],
        "A Python utility for translating active text between Turkish and "
        "English using global keyboard shortcuts on macOS."
    ),
}

# The profile intentionally showcases six projects. The repository and language
# charts still consider all public repositories.

# GitHub reports a custom or unrecognised licence as one of these. Printing
# "Other" next to a project says nothing, so it is dropped instead.
LICENCE_NOISE = {"NOASSERTION", "other", "Other", None, ""}


def day(iso):
    return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%d %b %Y")


def render_card(r, index):
    """One project card. Curated prose if there is any, the repo's own
    description if there is not — never an empty cell, and never a visibly
    second-class one."""
    name = r["name"]
    stack, blurb = CURATED.get(name, (None, None))

    if blurb is None:
        lang = (r["primaryLanguage"] or {}).get("name")
        topics = [t["topic"]["name"] for t in r["repositoryTopics"]["nodes"]]
        # A repo tagged "go" whose primary language is Go would otherwise read
        # "Go · go", so fold anything that differs only by case.
        stack, seen = [], set()
        for s in ([lang] if lang else []) + topics:
            if s.lower() not in seen:
                seen.add(s.lower())
                stack.append(s)
        stack = stack[:4]
        blurb = (r["description"] or "").strip() or "_No description yet._"

    meta = [" · ".join("`%s`" % s for s in stack)] if stack else []
    if r["stargazerCount"]:
        meta.append("%d star%s" % (r["stargazerCount"], "" if r["stargazerCount"] == 1 else "s"))
    spdx = (r["licenseInfo"] or {}).get("spdxId")
    if spdx not in LICENCE_NOISE:
        meta.append(spdx)
    if r["isArchived"]:
        meta.append("archived")

    # Dates, not "3 hours ago". A relative stamp would differ on almost every
    # run and the workflow would commit every ten minutes forever; a date only
    # changes when the repository owner actually pushes.
    foot = "%s → %s" % (day(r["createdAt"]), day(r["pushedAt"]))

    return "\n".join([
        "#### [%s](https://github.com/%s/%s)" % (name, USER, name),
        "<sub>%s</sub>" % " — ".join(meta),
        "",
        blurb,
        "",
        "<sub>%s</sub>" % foot,
    ])


def build_projects(repos):
    """A compact, recruiter-friendly grid of selected public projects."""
    by = {r["name"]: r for r in repos}
    ordered = [by[name] for name in CURATED if name in by]

    rows = []
    for i in range(0, len(ordered), 2):
        pair = ordered[i:i + 2]
        cells = ['<td width="50%" valign="top">\n\n' + render_card(r, i + j) + '\n\n</td>'
                 for j, r in enumerate(pair)]
        if len(pair) == 1:                      # odd count: keep the grid square
            cells.append('<td width="50%"></td>')
        rows.append("<tr>\n" + "\n".join(cells) + "\n</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


# --------------------------------------------------------------------------- figures

FIGURES = ("header",)

ALT = {
    "header": "Burak, @Burak-ML. AI automation and agentic systems; "
              "data science with Python and SQL.",
}


def figure(name):
    """A <picture> pairing the two themes. GitHub renders this natively, so the
    reader never gets the wrong one baked into an <img>."""
    asset = name
    return ("<picture>\n"
            '  <source media="(prefers-color-scheme: dark)" srcset="assets/%s-dark.svg">\n'
            '  <img alt="%s" src="assets/%s-light.svg" width="100%%">\n'
            "</picture>" % (asset, ALT[name], asset))


def render_figures(u, repos, projects, private):
    cc = u["contributionsCollection"]
    peak = max((d["contributionCount"]
                for w in cc["contributionCalendar"]["weeks"]
                for d in w["contributionDays"]), default=0)
    opened = u["createdAt"][:10]
    files = {}
    for theme in THEMES:
        files["header-%s.svg" % theme] = assets.build_header(theme, u, len(projects))
    return files, peak


# --------------------------------------------------------------------------- README

def replace_region(text, tag, body):
    pattern = r"<!--%s-->.*?<!--/%s-->" % (tag, tag)
    out, n = re.subn(pattern, lambda _: "<!--%s-->\n%s\n<!--/%s-->" % (tag, body, tag),
                     text, flags=re.S)
    if not n:
        print("WARNING: no <!--%s--> markers in README.md" % tag)
    return out


def update_readme(projects):
    """Rewrite the generated regions of README.md. Everything between a
    <!--tag--> pair is machine-owned; the prose around it is not touched."""
    if not os.path.exists(README):
        return False
    with open(README, encoding="utf-8") as f:
        before = f.read()

    after = replace_region(before, "projects", build_projects(projects))
    for name in FIGURES:
        after = replace_region(after, "fig-" + name, figure(name))

    if after == before:
        print("unchanged README.md")
        return False
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(after)
    print("updated README.md (%d project cards)" % len(projects))
    return True


# --------------------------------------------------------------------------- main

def main():
    u = fetch()
    repos = [r for r in u["repositories"]["nodes"] if not r["isFork"]]
    projects = [r for r in repos if r["name"].lower() != USER.lower()]
    cc = u["contributionsCollection"]

    # Which figure the contribution count is depends on the token, and the API
    # will not tell us: queried by the job's GITHUB_TOKEN, work in private repos
    # is simply absent and restrictedContributionsCount still comes back 0. So
    # the workflow sets COUNTS_PRIVATE when a personal token is configured, and
    # the label follows that rather than pretending to detect it.
    private = bool(os.environ.get("PROFILE_TOKEN") or os.environ.get("COUNTS_PRIVATE"))

    files, peak = render_figures(u, repos, projects, private)
    os.makedirs(OUT, exist_ok=True)
    for name, body in sorted(files.items()):
        path = os.path.join(OUT, name)
        old = ""
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                old = f.read()
        if old != body:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(body)
            print("updated %s" % name)
        else:
            print("unchanged %s" % name)

    update_readme(projects)
    print("contributions=%d commits=%d repos=%d peak=%d private_counted=%s"
          % (cc["contributionCalendar"]["totalContributions"],
             cc["totalCommitContributions"], len(repos), peak, private))


if __name__ == "__main__":
    main()
