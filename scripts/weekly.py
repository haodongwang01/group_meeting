"""Build the week and member views from the team's Markdown reports."""
from datetime import date, datetime, timedelta, timezone
from html import escape
import os
import re
from urllib.parse import quote, urlencode


START = date(2026, 11, 23)
WEEK = timedelta(days=7)
MEMBERS = {
    "王浩东": "wang-haodong", "林健": "lin-jian", "游嘉玮": "you-jiawei",
    "刘千里": "liu-qianli", "米家志": "mi-jiazhi", "胡揚嘉": "hu-yangjia",
    "陈钦德": "chen-qinde",
}
HEADINGS = ("本周进展", "问题或求助", "下周计划")


def current_monday():
    override = os.environ.get("WEEKLY_AS_OF")
    today = date.fromisoformat(override) if override else datetime.now(timezone(timedelta(hours=8))).date()
    return today - timedelta(days=today.weekday())


def week_label(monday):
    end = monday + timedelta(days=6)
    last = f"{end.day} 日" if monday.month == end.month else f"{end.month} 月 {end.day} 日"
    return f"{monday.year} 年 {monday.month} 月 {monday.day} 日 – {last}"


def inline(text):
    """Only explicit HTTP(S) material links produce markup."""
    parts = []
    start = 0
    for match in re.finditer(r"\[([^\]\n]+)\]\((https?://[^\s()<>\"']+)\)", text):
        parts.extend((escape(text[start:match.start()]),
                      f'<a href="{escape(match[2], quote=True)}">{escape(match[1])}</a>'))
        start = match.end()
    return "".join(parts) + escape(text[start:])


def blocks(lines):
    result = []
    paragraph = []
    items = []

    def flush():
        if paragraph:
            result.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()
        if items:
            result.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>")
            items.clear()

    for line in lines:
        if not line:
            flush()
        elif line.startswith(("- ", "* ")):
            if paragraph:
                flush()
            items.append(line[2:])
        else:
            if items:
                flush()
            paragraph.append(line)
    flush()
    return "".join(result)


def read_report(path, placeholder):
    text = re.sub(r"<!--.*?-->", "", path.read_text(encoding="utf-8-sig"), flags=re.S).strip()
    if not text:
        return None
    first, *rest = text.splitlines()
    if not first.startswith("# "):
        raise ValueError(f"{path}: 请以「# 一句话结论」开头")
    title = first[2:].strip()
    sections = {}
    heading = None
    for raw in rest:
        line = raw.strip()
        if line.startswith("## "):
            heading = line[3:].strip()
            if heading not in HEADINGS or heading in sections:
                raise ValueError(f"{path}: 未知或重复的小标题「{heading}」")
            sections[heading] = []
        elif heading is not None:
            sections[heading].append(line)
        elif line:
            raise ValueError(f"{path}: 请在「## 本周进展」下填写正文")
    if not any(any(lines) for lines in sections.values()):
        return None
    if not title or first == placeholder or set(sections) != set(HEADINGS) or not any(sections["本周进展"]):
        raise ValueError(f"{path}: 请填写一句话结论、本周进展，并保留模板的三个小标题")
    return title, {name: blocks(sections[name]) for name in HEADINGS}


def build_weekly(source, repo, shell, write):
    current = max(START, current_monday())
    weeks = [START + n * WEEK for n in reversed(range((current - START).days // 7 + 1))]
    template = (source / "TEMPLATE.md").read_text(encoding="utf-8").strip()
    reports = {}
    existing = set()
    for path in sorted(source.glob("*/*.md")):
        week = date.fromisoformat(path.parent.name)
        if week.isoformat() != path.parent.name or week.weekday() or week < START or path.stem not in MEMBERS:
            raise ValueError(f"{path}: 请使用周一日期和名单中的姓名")
        key = (week, path.stem)
        existing.add(key)
        report = read_report(path, template.splitlines()[0])
        if report:
            reports[key] = report

    guide = f"{repo}/blob/main/content/weekly/README.md"
    paths = []

    def publish(path, title, description, body):
        write(path, shell(title, description, f'<main id="main" class="wrap weekly-page">{body}</main>', path))
        paths.append(path)

    def count(week):
        return f"{sum((week, name) in reports for name in MEMBERS)}/{len(MEMBERS)} 人已更新"

    def entry(week, name):
        key = (week, name)
        filename = f"{week}/{name}.md"
        if key in existing:
            editor = f"{repo}/edit/main/content/weekly/{quote(filename)}"
        else:
            query = urlencode({"filename": "content/weekly/" + filename, "value": template + "\n"}, quote_via=quote)
            editor = f"{repo}/new/main?{query}"
        link = escape(editor, quote=True)
        if key not in reports:
            return f'<div class="w-empty"><span>待更新</span><a href="{link}" aria-label="填写{name}的周报">填写</a></div>'
        title, sections = reports[key]
        details = "".join(
            f'<div><dt>{h}</dt><dd>{sections[h] or "—"}</dd></div>' for h in HEADINGS
        )
        return (f'<details class="w-report"><summary>{escape(title)}</summary><dl>{details}</dl>'
                f'<a href="{link}">编辑周报</a></details>')

    def list_weeks(week):
        links = "".join(f'<a href="{w}.html"'
                        + (' aria-current="page"' if w == week else '')
                        + f'>{week_label(w)}</a>' for w in weeks)
        return f'<details class="w-weeks"><summary>切换周次</summary><nav aria-label="选择周次">{links}</nav></details>'

    for week in weeks:
        rows = "".join(
            f'<li><a class="w-name" href="members/{slug}.html">{name}</a>{entry(week, name)}</li>'
            for name, slug in MEMBERS.items()
        )
        body = (f'<header class="w-heading"><h1>组员周报</h1><a class="primary-link" href="{guide}">提交本周周报</a></header>'
                f'<section aria-label="全组周报"><div class="w-bar"><div><h2><a href="{week}.html">{week_label(week)}</a></h2>'
                f'<p>{count(week)}</p></div>{list_weeks(week)}</div><ul class="w-rows">{rows}</ul></section>')
        publish(f"weekly/{week}.html", week_label(week) + " · 组员周报", count(week), body)
        if week == current:
            publish("weekly/index.html", "组员周报", week_label(week) + " · " + count(week), body)

    for name, slug in MEMBERS.items():
        rows = "".join(
            f'<li><a class="w-date" href="../{week}.html">{week_label(week)}</a>{entry(week, name)}</li>'
            for week in weeks
        )
        body = (f'<a class="w-back" href="../index.html">← 全组周报</a><header class="w-heading"><h1>{name}的周报</h1></header>'
                f'<ul class="w-rows w-history">{rows}</ul>')
        publish(f"weekly/members/{slug}.html", f"{name}的周报", f"{name}历周的进展、问题与下周计划。", body)

    teaser = (f'<aside class="wrap w-teaser" aria-label="本周周报"><a href="weekly/index.html"><strong>本周周报</strong>'
              f'<span>{week_label(current)}</span><span>{count(current)}</span><b aria-hidden="true">→</b></a></aside>')
    return teaser, paths
