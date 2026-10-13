import json
import urllib.request
from datetime import datetime
from pathlib import Path

USERNAME = "daksh043"

contributions = []
total_count = 0
try:
    url = f"https://github-contributions-api.jogruber.de/v4/{USERNAME}?y=last"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        api_data = json.loads(resp.read().decode())
        contributions = api_data.get("contributions", [])
        total_count = sum(d.get("count", 0) for d in contributions)
except Exception as e:
    print(f"API fetch fallback: {e}")

if not contributions:
    data_path = Path("data/contributions.json")
    if not data_path.exists():
        data_path = Path("../daksh043/data/contributions.json")
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            local_data = json.load(f)
            contributions = local_data.get("days", [])
            total_count = local_data.get("total", len(contributions))

start_idx = 0
for i, d in enumerate(contributions):
    dt = datetime.fromisoformat(d["date"].replace("Z", "+00:00")) if "T" in d["date"] else datetime.strptime(d["date"], "%Y-%m-%d")
    if dt.weekday() == 6:  # Sunday
        start_idx = i
        break

aligned = contributions[start_idx:]
weeks = []
for i in range(0, len(aligned), 7):
    chunk = aligned[i:i+7]
    if len(chunk) == 7:
        weeks.append(chunk)

if len(weeks) > 52:
    weeks = weeks[-52:]

month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
month_labels = [None] * len(weeks)
last_month = None

for w_idx, week in enumerate(weeks):
    m_num = int(week[0]["date"].split("-")[1])
    if m_num != last_month:
        month_labels[w_idx] = month_names[m_num - 1]
        last_month = m_num

card_w = 860
card_h = 280
grid_x = 42
grid_y = 78
cell_size = 11.2
cell_gap = 3.6
rx = 3.2

COLORS = {
    0: "rgba(255, 255, 255, 0.12)",
    1: "#d9f2a6",
    2: "#b4e84c",
    3: "#8fc22f",
    4: "#5f8a14",
}

svg_lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {card_w} {card_h}" width="{card_w}" height="{card_h}">',
    '  <defs>',
    '    <linearGradient id="calamansi-bg" x1="0%" y1="0%" x2="100%" y2="100%">',
    '      <stop offset="0%" stop-color="#4e6854" />',
    '      <stop offset="50%" stop-color="#344e3d" />',
    '      <stop offset="100%" stop-color="#213326" />',
    '    </linearGradient>',
    '    <filter id="card-shadow" x="-5%" y="-5%" width="110%" height="115%">',
    '      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#000000" flood-opacity="0.4" />',
    '    </filter>',
    '    <filter id="drawer-shadow" x="-2%" y="-5%" width="104%" height="120%">',
    '      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000000" flood-opacity="0.45" />',
    '    </filter>',
    '  </defs>',
    '  <style>',
    '    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; font-size: 16px; font-weight: 700; fill: #ffffff; letter-spacing: -0.01em; }',
    '    .month { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 10px; font-weight: 500; fill: rgba(255, 255, 255, 0.5); }',
    '    .drawer-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 13px; font-weight: 600; fill: #ffffff; }',
    '    .badge-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; font-weight: 700; fill: #ffffff; text-anchor: middle; dominant-baseline: central; }',
    '  </style>',
    f'  <!-- Card Background -->',
    f'  <rect x="10" y="10" width="{card_w - 20}" height="{card_h - 20}" rx="28" fill="url(#calamansi-bg)" filter="url(#card-shadow)" stroke="rgba(255,255,255,0.12)" stroke-width="1" />',
    f'  <!-- Header Title -->',
    f'  <text x="{grid_x}" y="46" class="title">{total_count} contributions in 2026</text>',
]

for w_idx, label in enumerate(month_labels):
    if label:
        mx = grid_x + w_idx * (cell_size + cell_gap)
        svg_lines.append(f'  <text x="{mx:.1f}" y="68" class="month">{label}</text>')

for w_idx, week in enumerate(weeks):
    cx = grid_x + w_idx * (cell_size + cell_gap)
    for d_idx, day in enumerate(week):
        cy = grid_y + d_idx * (cell_size + cell_gap)
        lvl = day.get("level", 0)
        color = COLORS.get(lvl, COLORS[0])
        svg_lines.append(f'  <rect x="{cx:.1f}" y="{cy:.1f}" width="{cell_size:.1f}" height="{cell_size:.1f}" rx="{rx}" fill="{color}" />')

drawer_y = grid_y + 7 * (cell_size + cell_gap) + 16
drawer_w = card_w - 60
drawer_h = 44
drawer_x = 30

svg_lines.extend([
    f'  <!-- Bottom Drawer -->',
    f'  <rect x="{drawer_x}" y="{drawer_y}" width="{drawer_w}" height="{drawer_h}" rx="14" fill="#0d1711" fill-opacity="0.82" stroke="rgba(255,255,255,0.18)" stroke-width="1" filter="url(#drawer-shadow)" />',
    f'  <text x="{drawer_x + 18}" y="{drawer_y + 26}" class="drawer-text">Top contributions in:</text>',
    f'  <!-- Repo Badges -->',
    f'  <!-- Badge 1: P (PocketLedger) -->',
    f'  <circle cx="{drawer_x + drawer_w - 95}" cy="{drawer_y + 22}" r="12" fill="rgba(255,255,255,0.18)" stroke="#0d1711" stroke-width="2" />',
    f'  <text x="{drawer_x + drawer_w - 95}" y="{drawer_y + 22}" class="badge-text">P</text>',
    f'  <!-- Badge 2: D (Daksh043) -->',
    f'  <circle cx="{drawer_x + drawer_w - 75}" cy="{drawer_y + 22}" r="12" fill="#e11d48" stroke="#0d1711" stroke-width="2" />',
    f'  <text x="{drawer_x + drawer_w - 75}" y="{drawer_y + 22}" class="badge-text">D</text>',
    f'  <!-- Badge 3: A (AI-ConnectX) -->',
    f'  <circle cx="{drawer_x + drawer_w - 55}" cy="{drawer_y + 22}" r="12" fill="rgba(255,255,255,0.22)" stroke="#0d1711" stroke-width="2" />',
    f'  <text x="{drawer_x + drawer_w - 55}" y="{drawer_y + 22}" class="badge-text">A</text>',
    f'  <!-- Chevron Button -->',
    f'  <circle cx="{drawer_x + drawer_w - 24}" cy="{drawer_y + 22}" r="12" fill="rgba(255,255,255,0.12)" />',
    f'  <path d="M {drawer_x + drawer_w - 28} {drawer_y + 19} L {drawer_x + drawer_w - 24} {drawer_y + 23} L {drawer_x + drawer_w - 20} {drawer_y + 19}" fill="none" stroke="#ffffff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />',
    '</svg>',
])

svg_content = "\n".join(svg_lines)

out_dirs = [Path("."), Path("../daksh043")]
for d in out_dirs:
    target = d / "github-activity-card.svg"
    try:
        target.write_text(svg_content, encoding="utf-8")
        print(f"Generated {target.resolve()} ({len(svg_content)} bytes)")
    except Exception as e:
        print(f"Error writing to {target}: {e}")
