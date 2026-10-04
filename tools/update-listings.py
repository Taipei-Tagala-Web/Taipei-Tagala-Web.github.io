#!/usr/bin/env python3
"""
tools/update-listings.py
為 zh-TW / en / ja 的 meetings/index.html 每張活動卡加上個別頁連結，
並更新 sitemap.xml 加入所有個別頁的 URL。

執行方式（Windows PowerShell）：
  $env:PYTHONIOENCODING='utf-8'
  python tools/update-listings.py
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
    '2026-11-10': '20261110-if-i-had-an-ai-double-creating-time',
    '2026-11-24': '20261124-warmth-across-borders-borrowed-grandpa',
    '2026-12-08': '20261208-believe-in-goodness-iron-brigade',
    '2026-12-22': '20261222-aromatherapy-sleep',
}

# 列表頁的 FB 連結文字（因語系而異）
FB_LINK_TEXT = {
    'zh': 'Facebook 活動頁 →',
    'en': 'Event on Facebook →',
    'ja': 'Facebook イベントページ →',
}

MORE_TEXT = {
    'zh': '了解更多 →',
    'en': 'Read more →',
    'ja': '詳細を見る →',
}

LANG_DIR = {'zh': 'zh-TW', 'en': 'en', 'ja': 'ja'}


def update_listing(lang):
    ld   = LANG_DIR[lang]
    path = BASE / ld / 'meetings' / 'index.html'
    text = path.read_text(encoding='utf-8')
    changed = 0

    for ev in DATA['events']:
        ev_id  = ev['id']
        slug   = SLUGS.get(ev_id)
        if not slug:
            continue
        fb_url = ev.get('fbUrl', '')
        detail_url = f'/{ld}/meetings/2026/{slug}/'
        more_link  = f'<a href="{detail_url}">{MORE_TEXT[lang]}</a>'

        if fb_url:
            # 在現有的 FB 連結後面插入個別頁連結
            fb_text = FB_LINK_TEXT[lang]
            old_frag = f'<a href="{fb_url}" target="_blank" rel="noopener">{fb_text}</a></p>'
            new_frag = f'<a href="{fb_url}" target="_blank" rel="noopener">{fb_text}</a> {more_link}</p>'

            if old_frag in text:
                if new_frag not in text:   # 避免重複插入
                    text = text.replace(old_frag, new_frag, 1)
                    changed += 1
                    print(f'  [{ld}] 更新 {ev_id} (含 FB 連結)')
                else:
                    print(f'  [{ld}] 已存在 {ev_id}，跳過')
            else:
                print(f'  [{ld}] ⚠ 找不到 FB 連結段落: {ev_id}')
        else:
            # 無 FB 連結：在 event-body 的最後一個 <p> 後面插入 event-links
            # 用 title 文字定位：在該 h3 後方找到第一個 </div>\n        </article> 並插入
            title_zh = ev['title']['zh']
            # 改以 h3 的 zh 標題定位，再向後找 </div>\n        </article>
            # 策略：找到 </p>\n          </div>\n        </article> 且在 title 出現之後
            idx_title = text.find(ev['title'][lang])
            if idx_title == -1:
                print(f'  [{ld}] ⚠ 找不到標題，無法插入 {ev_id}')
                continue
            # 從 title 位置後面找 event-links 或 </div>\n        </article>
            search_from = idx_title
            close_pattern = '</p>\n          </div>\n        </article>'
            idx_close = text.find(close_pattern, search_from)
            if idx_close == -1:
                print(f'  [{ld}] ⚠ 找不到卡片結尾，無法插入 {ev_id}')
                continue
            event_links_p = f'\n            <p class="event-links">{more_link}</p>'
            # 檢查是否已有此連結
            if detail_url in text[idx_title:idx_close + 100]:
                print(f'  [{ld}] 已存在 {ev_id}，跳過')
                continue
            insert_pos = idx_close + len('</p>')
            text = text[:insert_pos] + event_links_p + text[insert_pos:]
            changed += 1
            print(f'  [{ld}] 新增 {ev_id} (無 FB 連結)')

    if changed:
        path.write_text(text, encoding='utf-8')
        print(f'  [{ld}] meetings/index.html 已儲存（{changed} 處修改）')
    else:
        print(f'  [{ld}] 無需修改')


def update_sitemap():
    """在 sitemap.xml 中加入所有個別頁的 URL（3 語系 × 13 場 = 39 筆）。"""
    path = BASE / 'sitemap.xml'
    text = path.read_text(encoding='utf-8')

    insert_before = '</urlset>'
    if insert_before not in text:
        print('⚠ sitemap.xml 格式錯誤，找不到 </urlset>')
        return

    new_entries = ''
    for ev in reversed(DATA['events']):   # 由舊到新排序（reversed = 最舊在前）
        ev_id = ev['id']
        slug  = SLUGS.get(ev_id)
        if not slug:
            continue
        # 三語系互指
        zh_url = f'https://tagala.org.tw/zh-TW/meetings/2026/{slug}/'
        en_url = f'https://tagala.org.tw/en/meetings/2026/{slug}/'
        ja_url = f'https://tagala.org.tw/ja/meetings/2026/{slug}/'
        for lang_url, hl in [(zh_url, 'zh-Hant'), (en_url, 'en'), (ja_url, 'ja')]:
            if lang_url in text:
                continue   # 已存在
            new_entries += f"""  <url>
    <loc>{lang_url}</loc>
    <xhtml:link rel="alternate" hreflang="zh-Hant" href="{zh_url}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{en_url}"/>
    <xhtml:link rel="alternate" hreflang="ja" href="{ja_url}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{zh_url}"/>
    <lastmod>2026-10-04</lastmod>
    <priority>0.8</priority>
  </url>\n"""

    if new_entries:
        text = text.replace(insert_before, new_entries + insert_before)
        path.write_text(text, encoding='utf-8')
        print(f'  sitemap.xml 已更新')
    else:
        print('  sitemap.xml 無需修改')


if __name__ == '__main__':
    print('=== 更新列表頁 ===')
    for lang in ['zh', 'en', 'ja']:
        update_listing(lang)

    print('\n=== 更新 sitemap ===')
    update_sitemap()

    print('\n完成。')
