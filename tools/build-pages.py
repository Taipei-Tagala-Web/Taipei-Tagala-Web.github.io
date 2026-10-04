#!/usr/bin/env python3
"""
tools/build-pages.py — 台北大加蚋扶輪社活動獨立頁產生器
讀取 content/events.json，為每場活動產生 zh-TW / en / ja 三語系獨立頁。

執行方式（Windows PowerShell）：
  $env:PYTHONIOENCODING='utf-8'
  python tools\build-pages.py

預設跳過已存在的頁面（不覆蓋手動修改）。加上 --force 強制重寫所有頁。
"""
import json, os, sys, html as htmllib, argparse
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

with open(BASE / 'content' / 'events.json', encoding='utf-8') as f:
    DATA = json.load(f)

# ──────────────────────────────────────────────────────────
# Slug 表：每場活動的 URL slug（目錄名稱）
# ──────────────────────────────────────────────────────────
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

# 例會編號（service/fellowship/joint 類型無編號）
MEETING_NUMBERS = {
    '2026-07-14': 221, '2026-07-28': 222, '2026-08-11': 223,
    '2026-08-25': 224, '2026-09-08': 225, '2026-09-22': 226,
    '2026-10-13': 227, '2026-10-27': 228, '2026-11-10': 229,
    '2026-11-24': 230, '2026-12-08': 231, '2026-12-22': 232,
}

WEEKDAYS = {
    'zh': ['一', '二', '三', '四', '五', '六', '日'],
    'en': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    'ja': ['月', '火', '水', '木', '金', '土', '日'],
}

LANG_DIR   = {'zh': 'zh-TW', 'en': 'en', 'ja': 'ja'}
LANG_CODE  = {'zh': 'zh-Hant-TW', 'en': 'en', 'ja': 'ja'}
HREFLANG   = {'zh': 'zh-Hant', 'en': 'en', 'ja': 'ja'}
OG_LOCALE  = {'zh': 'zh_TW', 'en': 'en_US', 'ja': 'ja_JP'}

FONT_LINK = {
    'zh': 'https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&family=Open+Sans:wght@400;700&display=swap',
    'en': 'https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;700&display=swap',
    'ja': 'https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&display=swap',
}

SITE_NAME = {
    'zh': '台北大加蚋扶輪社',
    'en': 'Rotary Club of Taipei Tagala',
    'ja': '台北大加蚋ロータリークラブ',
}

SKIP_TEXT   = {'zh': '跳至主要內容', 'en': 'Skip to content', 'ja': '本文へスキップ'}
MENU_OPEN   = {'zh': '開啟選單', 'en': 'Open menu', 'ja': 'メニューを開く'}
MENU_CLOSE  = {'zh': '關閉選單', 'en': 'Close menu', 'ja': 'メニューを閉じる'}
BRAND_LABEL = {
    'zh': '台北大加蚋扶輪社',
    'en': 'Rotary Club of Taipei Tagala',
    'ja': '台北大加蚋ロータリークラブ',
}
NAV_ARIA    = {'zh': '主要導覽', 'en': 'Main navigation', 'ja': 'メインナビゲーション'}
LANG_ARIA   = {'zh': '語言選擇', 'en': 'Language', 'ja': '言語選択'}
CURR_LANG   = {'zh': '中文', 'en': 'English', 'ja': '日本語'}

NAV_ITEMS = {
    'zh': [('首頁', '/zh-TW/'), ('關於我們', '/zh-TW/about/'), ('服務計畫', '/zh-TW/service/'),
           ('例會/活動', '/zh-TW/meetings/'), ('聯絡我們', '/zh-TW/contact/')],
    'en': [('Home', '/en/'), ('About', '/en/about/'), ('Service', '/en/service/'),
           ('Meetings', '/en/meetings/'), ('Contact', '/en/contact/')],
    'ja': [('ホーム', '/ja/'), ('クラブ紹介', '/ja/about/'), ('奉仕活動', '/ja/service/'),
           ('例会・行事', '/ja/meetings/'), ('お問い合わせ', '/ja/contact/')],
}

BC_ARIA     = {'zh': '路徑導覽', 'en': 'Breadcrumb', 'ja': 'パンくずリスト'}
BC_HOME     = {'zh': '首頁', 'en': 'Home', 'ja': 'ホーム'}
BC_MEETINGS = {'zh': '例會與活動', 'en': 'Meetings', 'ja': '例会・行事'}

TYPE_CSS   = {'regular': 'tag-regular', 'service': 'tag-service', 'fellowship': 'tag-fellowship', 'joint': 'tag-joint'}
TYPE_LABEL = {
    'zh': {'regular': '例會', 'service': '服務計畫', 'fellowship': '聯誼活動', 'joint': '聯合例會'},
    'en': {'regular': 'Regular meeting', 'service': 'Service project', 'fellowship': 'Fellowship', 'joint': 'Joint meeting'},
    'ja': {'regular': '例会', 'service': '奉仕プロジェクト', 'fellowship': '親睦活動', 'joint': '合同例会'},
}
MEET_NUM_LABEL = {
    'zh': lambda n: f'第{n}次例會',
    'en': lambda n: f'Meeting {n}',
    'ja': lambda n: f'第{n}次例会',
}

POINTS_H2 = {
    'zh': {'regular': '本次例會將探討', 'service': '活動亮點', 'fellowship': '活動亮點', 'joint': '本次聯合例會將探討'},
    'en': {'regular': "Topics we'll explore", 'service': 'Highlights', 'fellowship': 'Highlights', 'joint': "Topics we'll explore"},
    'ja': {'regular': 'この例会で探るテーマ', 'service': '見どころ', 'fellowship': '見どころ', 'joint': 'この例会で探るテーマ'},
}

SIDEBAR_TITLE = {'zh': '活動資訊', 'en': 'Event info', 'ja': '開催情報'}

FB_EVENT_TEXT = {
    'zh': '查看 Facebook 活動頁 →',
    'en': 'View on Facebook →',
    'ja': 'Facebook イベントページを見る →',
}

SIDEBAR_FB_TEXT = {
    'zh': '查看大加蚋臉書粉絲專頁',
    'en': 'Visit our Facebook Page',
    'ja': 'Facebook ページを見る',
}

RETURN_TEXT = {
    'zh': '← 返回例會列表',
    'en': '← Back to all meetings',
    'ja': '← 例会一覧に戻る',
}

REGULAR_VENUE = {
    'zh': '台北市松山區八德路四段 123-1 號 B1（捷運南京三民站步行約 5 分鐘）',
    'en': 'B1, No. 123-1, Sec. 4, Bade Rd., Songshan Dist., Taipei (5-min walk from MRT Nanjing Sanmin)',
    'ja': '台北市松山区八德路四段 123-1 号 B1（MRT 南京三民駅から徒歩約 5 分）',
}

REGULAR_FEE = {
    'zh': '費用 600 元。',
    'en': 'Admission NT$600.',
    'ja': '参加費 600 元。',
}

RSVP_BASE = {
    'zh': '報名請洽大加蚋社社友',
    'en': 'RSVP through a Tagala club member',
    'ja': 'ご参加はクラブ会員を通じてお申し込みください',
}

FOOTER_HTML = {
    'zh': """\
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img class="footer-qr" src="/assets/logo/tagala.org.tw-qr-code.png"
             width="1024" height="1024" loading="lazy" decoding="async"
             alt="台北大加蚋扶輪社官網 QR code，掃描後前往 tagala.org.tw">
        <div>
          <p class="name">台北大加蚋扶輪社</p>
          <p class="name-latin">Rotary Club of Taipei Tagala</p>
          <p class="meta">3523 地區第七分區　社號 90275<br>2019 年 6 月創社</p>
        </div>
      </div>

      <div>
        <h3>例會資訊</h3>
        <p>每月第二、第四週週二<br>台北市松山區八德路四段 123-1 號 B1<br>捷運南京三民站步行約 5 分鐘</p>
      </div>

      <div>
        <h3>相關連結</h3>
        <ul>
          <li><a href="https://www.facebook.com/TaipeiTagala/" target="_blank" rel="noopener">Facebook 專頁</a></li>
          <li><a href="https://www.rotary.org/" target="_blank" rel="noopener">國際扶輪</a></li>
          <li><a href="https://ri3523.org/" target="_blank" rel="noopener">國際扶輪 3523 地區</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-legal">
      <p>© 2026 台北大加蚋扶輪社</p>
      <p>Rotary、扶輪、扶輪徽章及相關標誌為國際扶輪之註冊商標，經授權使用。<br>活動宣傳圖由本社製作，講者影像經同意使用。</p>
    </div>
  </div>
</footer>""",
    'en': """\
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img class="footer-qr" src="/assets/logo/tagala.org.tw-qr-code.png"
             width="1024" height="1024" loading="lazy" decoding="async"
             alt="QR code for the Rotary Club of Taipei Tagala website, tagala.org.tw">
        <div>
          <p class="name">Rotary Club of Taipei Tagala</p>
          <p class="name-latin">Rotary Club of Taipei Tagala</p>
          <p class="meta">Area 7, District 3523　Club ID 90275<br>Chartered June 2019</p>
        </div>
      </div>

      <div>
        <h3>Meeting info</h3>
        <p>Second and fourth Tuesday of each month<br>B1, No. 123-1, Sec. 4, Bade Rd., Songshan Dist., Taipei City<br>About a 5-minute walk from MRT Nanjing Sanmin Station</p>
      </div>

      <div>
        <h3>Related links</h3>
        <ul>
          <li><a href="https://www.facebook.com/TaipeiTagala/" target="_blank" rel="noopener">Facebook page</a></li>
          <li><a href="https://www.rotary.org/" target="_blank" rel="noopener">Rotary International</a></li>
          <li><a href="https://ri3523.org/" target="_blank" rel="noopener">Rotary District 3523</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-legal">
      <p>© 2026 Rotary Club of Taipei Tagala</p>
      <p>Rotary, the Rotary Emblem and related marks are registered trademarks of Rotary International, used with permission.<br>Event artwork produced by this club; speaker images used with consent.</p>
    </div>
  </div>
</footer>""",
    'ja': """\
<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <img class="footer-qr" src="/assets/logo/tagala.org.tw-qr-code.png"
             width="1024" height="1024" loading="lazy" decoding="async"
             alt="台北大加蚋ロータリークラブ公式サイト（tagala.org.tw）の QR コード">
        <div>
          <p class="name"><ruby>台北大加蚋<rp>（</rp><rt>タイペイ・タガラ</rt><rp>）</rp></ruby>ロータリークラブ</p>
          <p class="name-latin">Rotary Club of Taipei Tagala</p>
          <p class="meta">第3523地区 第7分区　クラブ番号 90275<br>2019年6月チャーター</p>
        </div>
      </div>

      <div>
        <h3>例会情報</h3>
        <p>毎月第2・第4火曜日<br>台北市松山区八德路四段123-1号 B1<br>MRT 南京三民駅から徒歩約5分</p>
      </div>

      <div>
        <h3>関連リンク</h3>
        <ul>
          <li><a href="https://www.facebook.com/TaipeiTagala/" target="_blank" rel="noopener">Facebook ページ</a></li>
          <li><a href="https://www.rotary.org/" target="_blank" rel="noopener">国際ロータリー</a></li>
          <li><a href="https://ri3523.org/" target="_blank" rel="noopener">国際ロータリー第3523地区</a></li>
        </ul>
      </div>
    </div>

    <div class="footer-legal">
      <p>© 2026 台北大加蚋ロータリークラブ</p>
      <p>Rotary、ロータリー、ロータリー章および関連標章は国際ロータリーの登録商標であり、許諾を得て使用しています。<br>行事告知画像は当クラブが制作し、卓話者の写真は同意を得て使用しています。</p>
    </div>
  </div>
</footer>""",
}

# ──────────────────────────────────────────────────────────
# Helper functions
# ──────────────────────────────────────────────────────────

def fmt_date(date_str, lang):
    d = datetime.strptime(date_str, '%Y-%m-%d')
    wd = WEEKDAYS[lang][d.weekday()]
    y, m, day = d.year, str(d.month).zfill(2), str(d.day).zfill(2)
    if lang == 'en':
        return f'{y}.{m}.{day} ({wd})'
    return f'{y}.{m}.{day}（{wd}）'

def h(text):
    """HTML-escape a string for body text."""
    return htmllib.escape(str(text))

def sidebar_time(ev, lang):
    ts = ev.get('timeStart', '')
    tt = ev.get('timeTalk', '')
    te = ev.get('timeEnd', '')
    if tt:
        if lang == 'zh':
            return f'🍽 {ts} 自由交流及用餐、{tt} 例會開始、{te} 散會'
        elif lang == 'en':
            return f'🍽 {ts} Networking &amp; dinner, {tt} Meeting begins, {te} Close'
        else:
            return f'🍽 {ts} 交流・会食、{tt} 例会開始、{te} 閉会'
    else:
        if lang == 'zh':
            return f'🕐 {ts}–{te}'
        elif lang == 'en':
            return f'🕐 {ts}–{te}'
        else:
            return f'🕐 {ts}–{te}'

def sidebar_venue(ev, lang):
    if 'venue' in ev:
        return '📍 ' + h(ev['venue'][lang])
    return '📍 ' + h(REGULAR_VENUE[lang])

def sidebar_fee(ev, lang):
    if ev.get('type') == 'regular':
        return f'💰 {h(RSVP_BASE[lang])}，{h(REGULAR_FEE[lang])}'
    return f'💰 {h(RSVP_BASE[lang])}。'

# ──────────────────────────────────────────────────────────
# Page generator
# ──────────────────────────────────────────────────────────

def generate_page(ev, lang):
    ev_id   = ev['id']
    slug    = SLUGS[ev_id]
    ld      = LANG_DIR[lang]           # 'zh-TW', 'en', 'ja'
    url     = f'/{ld}/meetings/2026/{slug}/'
    canon   = f'https://tagala.org.tw{url}'
    ev_type = ev.get('type', 'regular')

    title_raw     = ev['title'][lang]
    summary_raw   = ev['summary'][lang]
    speaker_raw   = ev['speaker'][lang]
    spk_title_raw = ev['speakerTitle'][lang]
    banner        = ev.get('banner', f"evt-{ev_id}")
    fb_url        = ev.get('fbUrl', '')

    # ── page <title>
    meet_num = MEETING_NUMBERS.get(ev_id)
    if lang == 'zh':
        meet_lbl = f'第{meet_num}次例會' if meet_num else None
        page_title = f'{h(title_raw)}｜{meet_lbl}｜{SITE_NAME[lang]}' if meet_lbl else f'{h(title_raw)}｜{SITE_NAME[lang]}'
        og_title   = f'{h(title_raw)}｜{SITE_NAME[lang]}'
    elif lang == 'en':
        meet_lbl = f'Meeting {meet_num}' if meet_num else None
        page_title = f'{h(title_raw)} | {meet_lbl} | {SITE_NAME[lang]}' if meet_lbl else f'{h(title_raw)} | {SITE_NAME[lang]}'
        og_title   = f'{h(title_raw)} | {SITE_NAME[lang]}'
    else:
        meet_lbl = f'第{meet_num}次例会' if meet_num else None
        page_title = f'{h(title_raw)}｜{meet_lbl}｜{SITE_NAME[lang]}' if meet_lbl else f'{h(title_raw)}｜{SITE_NAME[lang]}'
        og_title   = f'{h(title_raw)}｜{SITE_NAME[lang]}'

    # ── meta description (first 150 chars of summary)
    meta_desc = h(summary_raw[:150])

    # ── hreflang links
    hlref = '\n'.join(
        f'<link rel="alternate" hreflang="{HREFLANG[l]}" href="https://tagala.org.tw/{LANG_DIR[l]}/meetings/2026/{slug}/">'
        for l in ['zh', 'en', 'ja']
    )
    hlref += f'\n<link rel="alternate" hreflang="x-default" href="https://tagala.org.tw/zh-TW/meetings/2026/{slug}/">'

    # ── nav
    nav_items_html = ''
    for label, href in NAV_ITEMS[lang]:
        cur = ' aria-current="page"' if href == f'/{ld}/meetings/' else ''
        nav_items_html += f'        <li><a href="{href}"{cur}>{label}</a></li>\n'

    # ── lang switch (current lang first, then others)
    others = [(l2, CURR_LANG[l2], LANG_DIR[l2]) for l2 in ['zh', 'en', 'ja'] if l2 != lang]
    lang_switch = f'      <a href="{url}" hreflang="{HREFLANG[lang]}" aria-current="true">{CURR_LANG[lang]}</a>\n'
    for l2, lbl2, ld2 in others:
        lang_switch += f'      <a href="/{ld2}/meetings/2026/{slug}/" hreflang="{HREFLANG[l2]}">{lbl2}</a>\n'

    # ── event meta line in article
    date_disp = fmt_date(ev_id, lang)
    type_css  = TYPE_CSS[ev_type]
    type_lbl  = TYPE_LABEL[lang][ev_type]
    if meet_lbl:
        event_meta = f'          <span class="meeting-number">{meet_lbl}</span>\n          <span class="event-date">{date_disp}</span>\n          <span class="tag {type_css}">{type_lbl}</span>'
    else:
        event_meta = f'          <span class="event-date">{date_disp}</span>\n          <span class="tag {type_css}">{type_lbl}</span>'

    # ── points
    pts = ev.get('points', {}).get(lang, [])
    pts_html = ''
    if pts:
        items = '\n'.join(f'            <li>{h(p)}</li>' for p in pts)
        pts_html = f'\n        <div class="event-points">\n          <h2>{POINTS_H2[lang][ev_type]}</h2>\n          <ul>\n{items}\n          </ul>\n        </div>'

    # ── FB event link (text link style)
    fb_link_html = ''
    if fb_url:
        fb_link_html = f'\n        <p class="event-fb-link"><a href="{fb_url}" target="_blank" rel="noopener">{FB_EVENT_TEXT[lang]}</a></p>'

    # ── sidebar
    time_str  = sidebar_time(ev, lang)
    venue_str = sidebar_venue(ev, lang)
    fee_str   = sidebar_fee(ev, lang)

    # ── breadcrumb current label
    bc_current = meet_lbl if meet_lbl else h(title_raw[:25] + ('…' if len(title_raw) > 25 else ''))

    # ── image alt
    img_alt = h(title_raw)

    # ── og:description
    og_desc = h(summary_raw[:200])

    # ──────────────────── assemble HTML ────────────────────
    doc = f"""\
<!DOCTYPE html>
<html lang="{LANG_CODE[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{page_title}</title>
<meta name="description" content="{meta_desc}">

<link rel="canonical" href="{canon}">
{hlref}

<meta property="og:type" content="article">
<meta property="og:locale" content="{OG_LOCALE[lang]}">
<meta property="og:url" content="{canon}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:image" content="https://tagala.org.tw/assets/events/{banner}.webp">

<link rel="icon" href="/assets/logo/favicon.ico" sizes="any">
<link rel="icon" href="/assets/logo/favicon-32.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/logo/apple-touch-icon.png">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONT_LINK[lang]}">
<link rel="stylesheet" href="/assets/css/tokens.css">
<link rel="stylesheet" href="/assets/css/main.css">
<noscript><style>@media (max-width:767.98px){{.main-nav{{position:static;opacity:1;visibility:visible;transform:none;background:none;padding:0;overflow:visible}}.main-nav a{{min-height:0;padding:var(--sp-2) 0;color:var(--c-heading);font-size:var(--fs-sm);border-bottom:0}}.nav-toggle{{display:none}}}}</style></noscript>
</head>
<body>

<a class="skip" href="#main">{SKIP_TEXT[lang]}</a>

<header class="site-header">
  <div class="container header-inner">
    <a class="brand" href="/{ld}/" aria-label="{BRAND_LABEL[lang]}">
      <img class="sig-wide" src="/assets/logo/signature-bilingual.webp"
           srcset="/assets/logo/signature-bilingual-320w.webp 320w, /assets/logo/signature-bilingual.webp 640w"
           sizes="232px" width="640" height="203" alt="{BRAND_LABEL[lang]}">
      <img class="sig-compact" src="/assets/logo/signature-compact.webp"
           srcset="/assets/logo/signature-compact-240w.webp 240w, /assets/logo/signature-compact.webp 480w"
           sizes="168px" width="480" height="202" alt="{BRAND_LABEL[lang]}">
    </a>

    <button class="nav-toggle" type="button"
            aria-controls="main-nav" aria-expanded="false"
            aria-label="{MENU_OPEN[lang]}"
            data-label-open="{MENU_OPEN[lang]}"
            data-label-close="{MENU_CLOSE[lang]}">
      <span class="nav-toggle-bars"></span>
    </button>

    <nav class="main-nav" id="main-nav" aria-label="{NAV_ARIA[lang]}">
      <ul>
{nav_items_html.rstrip()}
      </ul>
    </nav>

    <nav class="lang-switch" aria-label="{LANG_ARIA[lang]}">
{lang_switch.rstrip()}
    </nav>
  </div>
</header>

<main id="main">

  <div class="container">
    <nav class="breadcrumb" aria-label="{BC_ARIA[lang]}">
      <a href="/{ld}/">{BC_HOME[lang]}</a>
      <span aria-hidden="true">›</span>
      <a href="/{ld}/meetings/">{BC_MEETINGS[lang]}</a>
      <span aria-hidden="true">›</span>
      <span aria-current="page">{bc_current}</span>
    </nav>
  </div>

  <div class="container">
    <div class="event-hero">
      <img src="/assets/events/{banner}.webp"
           srcset="/assets/events/{banner}-600w.webp 600w, /assets/events/{banner}.webp 1200w"
           sizes="(min-width: 1080px) 1048px, calc(100vw - 32px)"
           width="1200" height="675" decoding="async"
           alt="{img_alt}">
    </div>
  </div>

  <div class="container">
    <div class="event-layout">

      <article class="event-detail">

        <p class="event-meta">
{event_meta}
        </p>

        <h1>{h(title_raw)}</h1>

        <p class="event-speaker">
          <b>{h(speaker_raw)}</b>
          {h(spk_title_raw)}
        </p>

        <p>{h(summary_raw)}</p>
{pts_html}
{fb_link_html}

      </article>

      <aside class="event-sidebar">
        <div class="event-info-box">
          <h3>{SIDEBAR_TITLE[lang]}</h3>
          <p>{time_str}</p>
          <p>{venue_str}</p>
          <p>{fee_str}</p>
          <a href="https://www.facebook.com/TaipeiTagala" target="_blank" rel="noopener" class="btn btn-facebook">{SIDEBAR_FB_TEXT[lang]}</a>
        </div>
      </aside>

    </div>
  </div>

  <div class="container">
    <div class="event-return">
      <a href="/{ld}/meetings/" class="btn btn-ghost">{RETURN_TEXT[lang]}</a>
    </div>
  </div>

</main>

{FOOTER_HTML[lang]}

<script src="/assets/js/nav.js" defer></script>

</body>
</html>
"""
    return doc


def run(force=False):
    today = datetime.today().strftime('%Y-%m-%d')
    written = 0
    skipped = 0

    for ev in DATA['events']:
        ev_id = ev['id']
        if ev_id not in SLUGS:
            print(f'  ⚠  no slug defined for {ev_id}, skipping')
            continue
        slug = SLUGS[ev_id]

        for lang in ['zh', 'en', 'ja']:
            ld  = LANG_DIR[lang]
            out = BASE / ld / 'meetings' / '2026' / slug / 'index.html'

            if out.exists() and not force:
                print(f'  skip  {ld}/meetings/2026/{slug}/ (already exists)')
                skipped += 1
                continue

            out.parent.mkdir(parents=True, exist_ok=True)
            html = generate_page(ev, lang)
            out.write_text(html, encoding='utf-8')
            print(f'  write {ld}/meetings/2026/{slug}/')
            written += 1

    print(f'\n完成：寫入 {written} 頁，跳過 {skipped} 頁。')
    if skipped:
        print('加上 --force 可強制重寫已存在的頁面。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='產生活動獨立頁')
    parser.add_argument('--force', action='store_true', help='覆蓋已存在的頁面')
    args = parser.parse_args()
    run(force=args.force)
