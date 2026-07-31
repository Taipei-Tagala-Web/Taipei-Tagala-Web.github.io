# 台北大加蚋扶輪社官網

## 專案性質

純靜態網站，GitHub Pages 託管。無後端、無資料庫、無 build step、無套件管理。
內容來自 `content/*.json`，HTML 由你依 JSON 產生後直接 commit。

## 語系與網址結構

三語系一對一，網址如下（**資料夾名稱固定，不得更動**）：

```
/                    語系偵測轉址（已寫好，勿改）
/zh-TW/              繁體中文  lang="zh-Hant-TW"  hreflang="zh-Hant"
/en/                 英文      lang="en"          hreflang="en"
/ja/                 日文      lang="ja"          hreflang="ja"
```

每個語系下五頁，slug 一致：
`index.html`、`about/index.html`、`service/index.html`、`meetings/index.html`、`contact/index.html`

注意 hreflang 用 `zh-Hant` 而非 `zh-TW`，涵蓋範圍較廣；資料夾名稱維持 `zh-TW`。
另需一組 `hreflang="x-default"` 指向 `/zh-TW/` 的對應頁。

## 絕對規則

1. 只用 HTML + CSS + 極少量原生 JS。**不引入任何框架、CDN 套件、npm 套件。**
2. 所有文字來自 `content/*.json`，不在 HTML 裡寫死文案。
3. 所有顏色、字級、間距只能用 `assets/css/tokens.css` 的 CSS 變數。**禁止寫死色碼。**
4. 三語系一對一。動到一頁就要同步三個語系，共 15 個內容頁。
5. **網站上不出現社友姓名，不出現大合照。** 講者姓名可出現（受邀外賓）。
6. 語言切換器必須連到「當前這一頁」的其他語系版本，不是連回首頁。
7. 每頁字型只載入該語系需要的：中文頁只載 Noto Sans TC，日文頁只載 Noto Sans JP，
   英文頁只載 Open Sans。**不可三種一起載。**

## 顏色使用硬規則（對比度實測結果）

國際扶輪 CI 禁止調整官方色，因此不能靠改深顏色解決對比度，只能改變用法：

| 用法 | 規則 |
|---|---|
| 配白字可用 | 皇室藍 9.19、紫 8.38、蔚藍 6.67、蔓越莓 4.93 |
| 配深墨字可用 | 金 7.62、天藍 6.26、橘 5.65 |
| **金色** | **絕不可作為白底上的文字色（1.99:1）**。只能當底色配皇室藍字，或作線條圖形 |
| **藍綠色** | **不可承載文字**（配白 3.49、配深墨 4.34 皆不足）。只能畫線與圖形 |

## 社徽使用規則

- 檔案只能用 `assets/logo/` 內的，**不得改色、變形、旋轉、加陰影、裁切**
- 淨空區不得小於「Rotary」文字標誌中大寫 R 的高度
- 齒輪（卓越標誌）不可單獨當裝飾或浮水印
- **現有社徽為透明去背版，只能用於淺色背景。**
  深藍底（如頁尾）上會失效：深藍字看不見、齒輪內部透空。
  在取得 Brand Center 反白版本前，**頁尾一律使用文字社名，不放社徽。**

## 圖片規則

活動 banner 全部已裁為 16:9，提供 1200w 與 600w 兩種尺寸：

```html
<img src="/assets/events/evt-2026-08-11.webp"
     srcset="/assets/events/evt-2026-08-11-600w.webp 600w,
             /assets/events/evt-2026-08-11.webp 1200w"
     sizes="(min-width: 768px) 560px, 100vw"
     width="1200" height="675" loading="lazy"
     alt="（依語系填入活動標題）">
```

每個 `<img>` 都必須有 `alt`（對應語系）、`width`、`height`。

## 日文特別規則

- 社名首次出現用 ruby：
  `<ruby>台北大加蚋<rp>（</rp><rt>タイペイ・タガラ</rt><rp>）</rp></ruby>ロータリークラブ`
- 例會演講一律用扶輪術語「卓話」，不用「講演」
- 服務一律用「奉仕」，不用「サービス」
- 用新字體「台北」，不用「臺北」
- 翻譯內容全部從 JSON 取，**不要自行重譯**

## 檔案結構

```
/                     index.html（轉址）、404.html、sitemap.xml、robots.txt、.nojekyll
/zh-TW/ /en/ /ja/     各五頁
/assets/css/          tokens.css（勿改）、main.css（你建立）
/assets/logo/         社徽與 favicon
/assets/brand/        club-flag.webp 社旗
/assets/events/       16 個活動 banner
/content/             site.json、events.json、service.json（唯一內容真相來源）
/tools/               check-i18n.py
START-HERE.html       建置操作手冊（Claude + GitHub 流程，給維護者看）
```

## 每次修改後必做

1. 執行三語系完整性檢查，必須通過。Windows PowerShell：

   ```powershell
   $env:PYTHONIOENCODING='utf-8'
   python tools\check-i18n.py
   ```

   **不要用 `python3`**（Windows 上是 Microsoft Store 轉接程式，會無聲結束）。
   **`PYTHONIOENCODING` 不可省略**，否則印出 ✓ 與中文時會以 `cp950` 編碼錯誤中斷。

2. 檢查 375px / 768px / 1280px 三個寬度無破版
3. 檢查三語系是否同步，語言切換器是否指向對應頁

## 版面既有決定（勿自行更動）

- **例會與活動頁**：「近期例會」與「過往活動」兩個區塊**使用同一種卡片版型**
  （`.event-card` 全套，含摘要），不做大小卡之分。
- 新頁面優先沿用既有 class；**需要新增 class 時先向使用者確認命名**，不要自行發明。
- HTML 不得寫死文案。JSON 缺的字串要補進 `content/site.json` 並標 `_verify`，
  再從 JSON 取用。
