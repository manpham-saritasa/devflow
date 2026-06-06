"""Log time to Jira via Tempo API + local log for daily totals."""

import base64
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timedelta

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
    )
)

LOGS_DIR = os.path.join(ROOT, ".local", "jiraflow", "logs")
TASKS_FILE = os.path.join(ROOT, ".local", "jiraflow", "favorite-tasks.txt")


def load_env():
    env = {}
    for fname in [".env.jira", ".env"]:
        path = os.path.join(ROOT, fname)
        if not os.path.exists(path):
            continue
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip().strip('"')
    return env


def parse_duration(value):
    value = value.lower().replace(" ", "")
    total = 0
    for part in re.findall(r"(\d+)(h|m)", value):
        amount = int(part[0])
        unit = part[1]
        total += amount * 3600 if unit == "h" else amount * 60
    if total == 0:
        raise ValueError(f"Invalid duration: {value}. Use 1h, 30m, 1h30m, or 2h 45m.")
    return total


def format_duration(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    if h and m:
        return f"{h}h {m}m"
    if h:
        return f"{h}h"
    return f"{m}m"


def parse_logged_seconds(time_str):
    total = 0
    for part in time_str.split():
        if part.endswith("h"):
            total += int(part[:-1]) * 3600
        elif part.endswith("m"):
            total += int(part[:-1]) * 60
    return total


def get_issue_summary(domain, auth, key):
    req = urllib.request.Request(
        f"https://{domain}.atlassian.net/rest/api/3/issue/{key}?fields=summary"
    )
    req.add_header("Authorization", f"Basic {auth}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["fields"]["summary"]


def get_issue_id(domain, auth, key):
    req = urllib.request.Request(
        f"https://{domain}.atlassian.net/rest/api/3/issue/{key}"
    )
    req.add_header("Authorization", f"Basic {auth}")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["id"]


def get_account_id(domain, auth):
    req = urllib.request.Request(f"https://{domain}.atlassian.net/rest/api/3/myself")
    req.add_header("Authorization", f"Basic {auth}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["accountId"]


def create_worklog(
    tempo_token,
    issue_id,
    seconds,
    description,
    account_id,
    job_type="Testingfunctionality",
    log_date=None,
):
    start_date = log_date if log_date else datetime.now().strftime("%Y-%m-%d")
    body = json.dumps(
        {
            "issueId": issue_id,
            "timeSpentSeconds": seconds,
            "startDate": start_date,
            "startTime": datetime.now().strftime("%H:%M:%S"),
            "description": description,
            "authorAccountId": account_id,
            "attributes": [{"key": "_JobType_", "value": job_type}],
        }
    ).encode()
    req = urllib.request.Request("https://api.tempo.io/4/worklogs", data=body)
    req.add_header("Authorization", f"Bearer {tempo_token}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def save_log(date_str, key, summary, seconds, description, domain):
    os.makedirs(LOGS_DIR, exist_ok=True)
    path = os.path.join(LOGS_DIR, f"{date_str}.md")
    is_new = not os.path.exists(path) or os.path.getsize(path) == 0
    time_str = format_duration(seconds)
    line = f"| [{key}](https://{domain}.atlassian.net/browse/{key}) | {summary} | {time_str} | {description} |\n"
    with open(path, "a", encoding="utf-8") as f:
        if is_new:
            f.write(f"# Worklogs for {date_str}\n\n")
            f.write("| Task | Title | Hours | Description |\n")
            f.write("| --- | --- | --- | --- |\n")
        f.write(line)


def read_logs(date_str):
    path = os.path.join(LOGS_DIR, f"{date_str}.md")
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip header lines
            if (
                line.startswith("#")
                or line.startswith("| -")
                or line == "| Task | Title | Hours | Description |"
            ):
                continue
            if line.startswith("|") and "|" in line[1:]:
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 4:
                    # Extract key from markdown link [KEY](url)
                    key = parts[0]
                    m = re.match(r"\[(.+?)\]\(", key)
                    if m:
                        key = m.group(1)
                    entries.append({"key": key, "time": parts[2], "desc": parts[3]})
    return entries


def show_today(domain, date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    entries = read_logs(date_str)
    if not entries:
        print(f"No logged time on {date_str}.")
        return

    total_seconds = sum(parse_logged_seconds(e["time"]) for e in entries)
    print(f"## {date_str}: {format_duration(total_seconds)} ({len(entries)} entries)\n")
    print("| # | Issue | Time | Description |")
    print("|---|-------|------|-------------|")
    for i, e in enumerate(reversed(entries), 1):
        print(
            f"| {i} | [{e['key']}](https://{domain}.atlassian.net/browse/{e['key']}) | {e['time']} | {e['desc']} |"
        )

    if total_seconds < 8 * 3600:
        missing = format_duration(8 * 3600 - total_seconds)
        print(
            f"\n  {date_str}: {format_duration(total_seconds)} logged - {missing} short of 8h"
        )


def show_task_list():
    if not os.path.exists(TASKS_FILE):
        print("No tasks.txt found.")
        return
    print("| # | Task |")
    print("|---|------|")
    with open(TASKS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.match(r"(\d+)\. (.+)", line)
            if m:
                num = m.group(1)
                rest = m.group(2)
                key_match = re.search(r"\[([A-Z0-9]+-\d+)\]\((.+?)\)", rest)
                if key_match:
                    task_url = key_match.group(2)
                    label = rest[: rest.index(" [")].strip()
                    print(f"| {num} | [{label}]({task_url}) |")
                else:
                    print(f"| {num} | {rest} |")


def resolve_key(arg):
    if arg.isdigit():
        if not os.path.exists(TASKS_FILE):
            print(f"Task #{arg} not found — no tasks.txt")
            sys.exit(1)
        with open(TASKS_FILE, encoding="utf-8") as f:
            for line in f:
                m = re.match(rf"^{arg}\.", line.strip())
                if m:
                    key_match = re.search(r"\[([A-Z0-9]+-\d+)\]", line)
                    if key_match:
                        return key_match.group(1)
        print(f"Task #{arg} not found in tasks.txt")
        sys.exit(1)
    return arg.upper()


def show_week():
    today = datetime.now().date()
    monday = today - timedelta(days=today.weekday())
    days = [(monday + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    projects = {}  # {project: {date_str: seconds}}
    for date_str in days:
        entries = read_logs(date_str)
        for e in entries:
            # Extract project from key (e.g., RMASUP-1 → RMASUP)
            key = e["key"]
            m = re.match(r"([A-Z]+)-", key)
            proj = m.group(1) if m else key
            if proj not in projects:
                projects[proj] = {d: 0 for d in days}
            projects[proj][date_str] += parse_logged_seconds(e["time"])

    if not projects:
        print("No logged time this week.")
        return

    sorted_projects = sorted(projects.keys())

    # Table header
    header = "| Project | " + " | ".join(day_labels) + " | Total |"
    sep = "|---" * (9) + "|"
    print(header)
    print(sep)

    day_totals = {d: 0 for d in days}
    grand_total = 0

    for proj in sorted_projects:
        row_total = sum(projects[proj].values())
        grand_total += row_total
        cells = [f"**{proj}**"]
        for d in days:
            secs = projects[proj][d]
            day_totals[d] += secs
            cells.append(format_duration(secs) if secs else "—")
        cells.append(format_duration(row_total))
        print("| " + " | ".join(cells) + " |")

    # Total row
    total_cells = ["**Total**"]
    for d in days:
        total_cells.append(format_duration(day_totals[d]) if day_totals[d] else "—")
    total_cells.append(format_duration(grand_total))
    print("| " + " | ".join(total_cells) + " |")

    # Flag days under 8h
    for i, d in enumerate(days):
        if day_totals[d] == 0:
            continue
        if day_totals[d] < 8 * 3600:
            missing = format_duration(8 * 3600 - day_totals[d])
            logged = format_duration(day_totals[d])
            print(f"  {day_labels[i]} {d}: {logged} logged - {missing} short of 8h")


def show_month():
    today = datetime.now().date()
    month_start = today.replace(day=1)
    days = []
    d = month_start
    while d <= today:
        days.append(d.strftime("%Y-%m-%d"))
        d += timedelta(days=1)

    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    weeks = {}
    day_totals = {}
    for date_str in days:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        week_num = dt.isocalendar()[1]
        if week_num not in weeks:
            weeks[week_num] = {}
        entries = read_logs(date_str)
        total = sum(parse_logged_seconds(e["time"]) for e in entries)
        weeks[week_num][date_str] = total
        day_totals[date_str] = total

    if not weeks:
        print("No logged time this month.")
        return

    print(f"## {today.strftime('%B %Y')} - up to {today.strftime('%b %d')}")
    print()

    header = "| Week | " + " | ".join(day_labels) + " | Total |"
    sep = "|---" * 9 + "|"
    print(header)
    print(sep)

    month_total = 0
    for week_num in sorted(weeks.keys()):
        week_data = weeks[week_num]
        dates_in_week = sorted(week_data.keys())
        week_start = datetime.strptime(dates_in_week[0], "%Y-%m-%d").date()
        week_end = datetime.strptime(dates_in_week[-1], "%Y-%m-%d").date()
        label = f"{week_start.strftime('%b %d')}-{week_end.strftime('%d')}"

        row_total = sum(week_data.values())
        month_total += row_total
        cells = [label]
        for i in range(7):
            # Calculate the date for this weekday in this week
            target_dt = week_start + timedelta(days=(i - week_start.weekday()))
            target_str = target_dt.strftime("%Y-%m-%d")
            if target_str in week_data:
                secs = week_data[target_str]
                cells.append(format_duration(secs) if secs else "-")
            elif target_dt > today:
                cells.append("")
            else:
                cells.append("-")
        cells.append(format_duration(row_total))
        print("| " + " | ".join(cells) + " |")

    total_cells = ["**Total**"]
    for i in range(7):
        wd_total = 0
        for date_str, secs in day_totals.items():
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            if dt.weekday() == i:
                wd_total += secs
        total_cells.append(format_duration(wd_total) if wd_total else "-")
    total_cells.append(format_duration(month_total))
    print("| " + " | ".join(total_cells) + " |")

    print()
    for date_str in days:
        secs = day_totals.get(date_str, 0)
        if secs == 0:
            continue
        if secs < 8 * 3600:
            dt = datetime.strptime(date_str, "%Y-%m-%d").date()
            label = day_labels[dt.weekday()]
            missing = format_duration(8 * 3600 - secs)
            print(
                f"  {label} {date_str}: {format_duration(secs)} logged - {missing} short of 8h"
            )


def main():
    if (
        "--help" in sys.argv
        or "-h" in sys.argv
        or (len(sys.argv) == 2 and sys.argv[1].lower() == "help")
    ):
        print(
            "Usage: python main.py <KEY> <DURATION> <DESCRIPTION> [--job TYPE] [--date DATE]"
        )
        print()
        print("Examples:")
        print("  jlog                              Show today's hours")
        print("  jlog week                         Show weekly project breakdown")
        print("  jlog month                        Show month view with weekly totals")
        print("  jlog mon                          Show Monday's details (mon-sun)")
        print("  jlog list                         Show quick-pick task list")
        print("  jlog PROJ-1 30m Email handle     Log 30 minutes")
        print("  jlog PROJ-1 1h Code review       Log 1 hour")
        print('  jlog PROJ-1 1h --job Dev "Coding"  Log with job type')
        print('  jlog PROJ-1 30m --date 6/1 "Meeting"  Log for specific date')
        print()
        print("Options:")
        print(
            "  --job TYPE      Job type (default: $JLOG_JOB_TYPE or Testingfunctionality)"
        )
        print(
            "  --date M/D      Log for specific date (auto-converts M/D, YYYY-MM-DD, YYYY/M/D)"
        )
        return

    if len(sys.argv) < 4:
        day_map = {
            "mon": 0,
            "monday": 0,
            "tue": 1,
            "tuesday": 1,
            "wed": 2,
            "wednesday": 2,
            "thu": 3,
            "thursday": 3,
            "fri": 4,
            "friday": 4,
            "sat": 5,
            "saturday": 5,
            "sun": 6,
            "sunday": 6,
        }
        if len(sys.argv) == 2 and sys.argv[1].lower() in day_map:
            env = load_env()
            today = datetime.now().date()
            monday = today - timedelta(days=today.weekday())
            target = monday + timedelta(days=day_map[sys.argv[1].lower()])
            show_today(env["JIRA_COMPANY_DOMAIN"], target.strftime("%Y-%m-%d"))
            return
        if len(sys.argv) == 2 and sys.argv[1] == "list":
            show_task_list()
            return
        if len(sys.argv) == 2 and sys.argv[1] == "week":
            show_week()
            return
        if len(sys.argv) == 2 and sys.argv[1] == "month":
            show_month()
            return
        env = load_env()
        show_today(env["JIRA_COMPANY_DOMAIN"])
        return

    key = resolve_key(sys.argv[1])
    duration_str = sys.argv[2]

    # Parse --job TYPE
    job_type = load_env().get("JLOG_JOB_TYPE", "Testingfunctionality")
    desc_start = 3
    if "--job" in sys.argv:
        idx = sys.argv.index("--job")
        if idx + 1 < len(sys.argv):
            job_type = sys.argv[idx + 1]
            # Skip --job and its value from description, regardless of position
            if idx <= desc_start:
                desc_start = max(desc_start, idx + 2)

    # Parse --date M/D or YYYY-MM-DD (auto-convert any format)
    log_date = datetime.now().strftime("%Y-%m-%d")
    if "--date" in sys.argv:
        idx = sys.argv.index("--date")
        if idx + 1 < len(sys.argv):
            date_str = sys.argv[idx + 1]
            # Auto-convert M/D, YYYY-MM-DD, or YYYY/M/D
            if "-" in date_str:
                parts = date_str.split("-")
                if len(parts) == 3 and all(p.isdigit() for p in parts):
                    log_date = (
                        f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
                    )
                else:
                    print(f"Invalid date format: {date_str}. Use M/D or YYYY-MM-DD.")
                    sys.exit(1)
            elif "/" in date_str:
                parts = date_str.split("/")
                if len(parts) in (2, 3) and all(p.isdigit() for p in parts):
                    if len(parts) == 3:
                        log_date = f"{int(parts[0]):04d}-{int(parts[1]):02d}-{int(parts[2]):02d}"
                    else:
                        log_date = f"{datetime.now().year}-{int(parts[0]):02d}-{int(parts[1]):02d}"
                else:
                    print(f"Invalid date format: {date_str}. Use M/D or YYYY-MM-DD.")
                    sys.exit(1)
            else:
                print(f"Invalid date format: {date_str}. Use M/D or YYYY-MM-DD.")
                sys.exit(1)
            # Skip --date and its value from description, regardless of position
            if idx <= desc_start:
                desc_start = max(desc_start, idx + 2)

    description = " ".join(sys.argv[desc_start:])
    seconds = parse_duration(duration_str)

    env = load_env()
    domain = env["JIRA_COMPANY_DOMAIN"]
    email = env["JIRA_EMAIL"]
    jira_token = env["JIRA_API_TOKEN"]
    tempo_token = env.get("TEMPO_API_TOKEN", "")
    if not tempo_token:
        print("Missing TEMPO_API_TOKEN in .env.jira. Cannot log time without it.")
        sys.exit(1)
    auth = base64.b64encode(f"{email}:{jira_token}".encode()).decode()

    issue_id = get_issue_id(domain, auth, key)
    summary = get_issue_summary(domain, auth, key)
    account_id = get_account_id(domain, auth)

    result = create_worklog(
        tempo_token, issue_id, seconds, description, account_id, job_type, log_date
    )
    save_log(log_date, key, summary, seconds, description, domain)

    print(
        f'✅ Logged {format_duration(seconds)} to [{key}](https://{domain}.atlassian.net/browse/{key}) — "{description}"'
    )
    print(f"   tempoWorklogId: {result['tempoWorklogId']}\n")

    show_today(domain, log_date)


if __name__ == "__main__":
    main()
