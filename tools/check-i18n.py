#!/usr/bin/env python3
"""三語系完整性檢查。上線前必跑。缺一個語系就 exit 1。"""
import json, sys, glob, os

LANGS = {'zh', 'en', 'ja'}

# 刻意只有單一語系的欄位（例如日文專用的 ruby 讀音）
SINGLE_LANG_OK = {
    'club.nameRuby',        # 日文 ruby 註記，中英文不需要
    'club.formalCitation',  # 日文姊妹社正式引用格式
}

problems = []

def walk(node, path, file):
    if isinstance(node, dict):
        keys = set(node.keys())
        # 判定：這個 dict 是不是一組語系值？
        if keys & LANGS:
            if path in SINGLE_LANG_OK:
                return
            missing = LANGS - keys
            if missing:
                problems.append(f'{file} :: {path} 缺少 {sorted(missing)}')
            for l in LANGS & keys:
                v = node[l]
                if isinstance(v, str) and not v.strip():
                    problems.append(f'{file} :: {path}.{l} 是空字串')
            extra = keys - LANGS
            if extra and not all(k.startswith('_') for k in extra):
                pass
            return
        for k, v in node.items():
            if k.startswith('_'):
                continue
            walk(v, f'{path}.{k}' if path else k, file)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f'{path}[{i}]', file)

for f in sorted(glob.glob('content/*.json')):
    try:
        data = json.load(open(f, encoding='utf-8'))
    except json.JSONDecodeError as e:
        problems.append(f'{f} :: JSON 格式錯誤 — {e}')
        continue
    walk(data, '', os.path.basename(f))

# 額外檢查：每個活動的 banner 檔案是否存在
try:
    ev = json.load(open('content/events.json', encoding='utf-8'))['events']
    for e in ev:
        for suffix in ('', '-600w'):
            p = f"assets/events/{e['banner']}{suffix}.webp"
            if not os.path.exists(p):
                problems.append(f"events.json :: {e['id']} 找不到圖檔 {p}")
except Exception as e:
    problems.append(f'events.json :: 讀取失敗 {e}')

if problems:
    print(f'✗ 發現 {len(problems)} 個問題：\n')
    for p in problems:
        print('  •', p)
    sys.exit(1)

ev = json.load(open('content/events.json', encoding='utf-8'))['events']
print(f'✓ 三語系完整性檢查通過')
print(f'  活動筆數：{len(ev)}（圖檔 {len(ev)*2} 個皆存在）')
print(f'  日期範圍：{min(e["date"] for e in ev)} ~ {max(e["date"] for e in ev)}')
