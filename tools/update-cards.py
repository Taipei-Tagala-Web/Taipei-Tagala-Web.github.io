#!/usr/bin/env python3
"""
tools/update-cards.py
對首頁與例會列表頁的每張活動卡做四項調整：
  1. 在 event-meta 加上例會代碼 (第 N 次例會)
  2. 移除 FB 連結，event-links 只留「了解更多 →」
  3. Banner 圖片包入連到個別例會頁的 <a>
  4. h3 標題文字包入同一連結

執行方式 (Windows PowerShell):
  $env:PYTHONIOENCODING='utf-8'
  python tools/update-cards.py
"""
import json, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

with open(BASE / 'content' / 'events.json', encoding='utf-8') as f:
    DATA = json.load(f)

SLUGS = {
    '2026-07-14': '20260714-giving-childhood-back-playground',
    '2026-07-28': '20260728-power-of-culture-migrants-literature-award',
    '2026-08-11': '20260811-formosa-goose-model-taiwanese-farming',
    '2026-08-25': '20260825-nostalgia-invention-fruit-chilli-sauce',
    '2026-09-08': '20260908-climate-change-net-zero-taiwan-agriculture',
    '2026-09-22': '20260922-nonprofit-newsroom-amplifier-for-the-unheard',
    '2026-10-13': '20261013-like-mindedness-middle-power-moment-marcin-jerzewski',
    '2026-10-27': '20261027-ten-reasons-pansci-became-a-youtuber',
    '2026-10-31': '20261031-when-rotary-meets-saigon',
    '2026-11-10': '20261110-if-i-had-an-ai-digital-twin',
    '2026-11-24': '20261124-warmth-across-borders-borrowed-grandpa',
    '2026-12-08': '20261208-believe-in-goodness-iron-brigade',
    '2026-12-22': '20261222-aromatherapy-sleep',
}

MEETING_NUMBERS = {
    '2026-07-14': 221, '2026-07-28': 222, '2026-08-11': 223,
    '2026-08-25': 224, '2026-09-08': 225, '2026-09-22': 226,
    '2026-10-13': 227, '2026-10-27': 228, '2026-11-10': 229,
    '2026-11-24': 230, '2026-12-08': 231, '2026-12-22': 232,
}

def meeting_num_text(lang, n):
    if lang == 'en': return f'Meeting {n}'
    if lang == 'ja': return f'第{n}次例会'
    return f'第{n}次例會'

MORE_TEXT = {'zh': '了解更多 →', 'en': 'Read more →', 'ja': '詳細を見る →'}
LANG_DIR  = {'zh': 'zh-TW', 'en': 'en', 'ja': 'ja'}

FILES = {
    'zh': ['zh-TW/meetings/index.html', 'zh-TW/index.html'],
    'en': ['en/meetings/index.html',    'en/index.html'],
    'ja': ['ja/meetings/index.html',    'ja/index.html'],
}


def transform_card(card_html, lang, ev_id, detail_url):
    """Apply four transformations to a single event-card HTML block."""
    out = card_html

    # ── 1. Add meeting number ────────────────────────────────────────────
    num = MEETING_NUMBERS.get(ev_id)
    if num:
        num_span = f'<span class="meeting-number">{meeting_num_text(lang, num)}</span>'
        date_tag = '<span class="event-date">'
        if num_span not in out:
            out = out.replace(date_tag, num_span + '\n              ' + date_tag, 1)

    # ── 2. event-links: remove FB, keep/add 了解更多 ──────────────────────
    more_link = f'<a href="{detail_url}">{MORE_TEXT[lang]}</a>'
    new_links  = f'<p class="event-links">{more_link}</p>'

    links_match = re.search(r'<p class="event-links">.*?</p>', out, re.DOTALL)
    if links_match:
        out = out[:links_match.start()] + new_links + out[links_match.end():]
    else:
        # 07/14 already has the link from update-listings; shouldn't reach here, but just in case
        close = '          </div>\n        </article>'
        if close in out:
            out = out.replace(close,
                              f'            {new_links}\n{close}', 1)

    # ── 3. Wrap banner img in <a> ────────────────────────────────────────
    banner_open = '<div class="banner">'
    banner_open_idx = out.find(banner_open)
    if banner_open_idx != -1:
        inner_start = banner_open_idx + len(banner_open)
        # find first </div> after banner opening
        inner_end = out.find('</div>', inner_start)
        if inner_end != -1:
            inner = out[inner_start:inner_end]
            if f'href="{detail_url}"' not in inner:
                wrapped = f'<a href="{detail_url}">{inner.strip()}</a>'
                out = (out[:inner_start]
                       + '\n            ' + wrapped + '\n          '
                       + out[inner_end:])

    # ── 4. Wrap h3 text in <a> ───────────────────────────────────────────
    h3_match = re.search(r'<h3>((?!<a[ >]).+?)</h3>', out, re.DOTALL)
    if h3_match:
        link_h3 = f'<h3><a href="{detail_url}">{h3_match.group(1)}</a></h3>'
        out = out[:h3_match.start()] + link_h3 + out[h3_match.end():]

    return out


def process_file(lang, rel_path):
    path = BASE / rel_path
    if not path.exists():
        print(f'  ⚠ 找不到: {rel_path}')
        return

    text = path.read_text(encoding='utf-8')
    ld   = LANG_DIR[lang]
    changed = 0

    for ev in DATA['events']:
        ev_id = ev['id']
        slug  = SLUGS.get(ev_id)
        if not slug:
            continue

        title = ev['title'][lang]
        if title not in text:
            continue

        detail_url = f'/{ld}/meetings/2026/{slug}/'

        # Locate the article boundaries
        title_idx   = text.find(title)
        art_start   = text.rfind('<article class="event-card">', 0, title_idx)
        art_end_tag = text.find('</article>', title_idx)
        if art_start == -1 or art_end_tag == -1:
            print(f'  ⚠ 找不到卡片邊界: {ev_id} in {rel_path}')
            continue
        art_end = art_end_tag + len('</article>')

        card_html = text[art_start:art_end]
        new_card  = transform_card(card_html, lang, ev_id, detail_url)

        if new_card != card_html:
            text    = text[:art_start] + new_card + text[art_end:]
            changed += 1
            print(f'  [{rel_path}] ✓ {ev_id}')

    if changed:
        path.write_text(text, encoding='utf-8')
        print(f'  [{rel_path}] 已儲存（{changed} 處修改）')
    else:
        print(f'  [{rel_path}] 無需修改')


if __name__ == '__main__':
    for lang, files in FILES.items():
        for rel_path in files:
            process_file(lang, rel_path)
    print('\n完成。')
