# FUMI OFFICIAL FANCLUB — Wireframes

`pyoeunji.com` の構造分析をもとに、**FUMI OFFICIAL FANCLUB** 用ワイヤーフレームを設計したドキュメントです。
低忠実度の HTML モック（4 ページ）と、本書の ASCII ワイヤーフレーム（全 7+ ページ）で構成されています。

> 設計判断はすべて **弁証法（正・反・合）** で導出しています。各意思決定の経緯は本書末尾の「設計判断ログ」を参照。

---

## 1. 分析対象サイト概要

**pyoeunji.com / PYO EUNJI OFFICIAL FANCLUB**

- 韓国モデル・女優 표은지（Pyo Eunji）の公式ファンクラブサイト
- **Shopify ベース**、日本語（`/`）と英語（`/en`）のマルチリンガル対応
- 機能: コンテンツ配信（プロフィール／ニュース）＋ EC（Shop）＋ 会員機能
- 会員モデル: 月額 ¥1,000 / 年額 ¥12,000（税込）。年会員は限定グッズ抽選優先

### サイトマップ

```
ROOT
├─ CONTENT (Home /en)            ← ヒーロー / 最新ニュース / 注目商品 / 会員CTA
├─ PROFILE      /pages/profile
├─ NEWS         /pages/news
├─ SHOP         /pages/shop → /collections /collections/all
│   └─ Product  /products/*
├─ FAQ          /pages/faq
├─ Account
│   ├─ Login    /account/login
│   └─ Register /account/register
└─ Footer
    ├─ ABOUT                /pages/about
    ├─ CONTACT
    ├─ MEMBERSHIP AGREEMENT
    ├─ PRIVACY POLICY       /pages/pp
    ├─ 特商法                /pages/scc
    └─ Q&A                  /pages/faq
```

### グローバル要素

- **Header**: `LOGO | CONTENT | PROFILE | SHOP | NEWS | [Lang切替] | FANCLUB LOGIN | BECOME A MEMBER`
- **Footer**: `Contact / About / Membership Agreement / Privacy Policy / 特商法 / Q&A` + SNS（Instagram / YouTube / X）+ © 表記

---

## 2. ページ別ワイヤーフレーム

各ページは ASCII 図 + 主要要素仕様で記載。HTML モックがあるページは末尾にリンクを示します。

### 2.1 Home `/` (CONTENT)  [→ `index.html`](./index.html)

```
┌────────────────────────────────────────────────────────────────────┐
│ [LOGO]   CONTENT  PROFILE  SHOP  NEWS   JP/EN  LOGIN  [JOIN]       │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│              [ HERO IMAGE — full-bleed key visual ]                │
│                  FUMI OFFICIAL FANCLUB                             │
│                       [ BECOME A MEMBER ]                          │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│ NEWS                                              [View all →]     │
│ ┌────────┐  ┌────────┐  ┌────────┐                                │
│ │ thumb  │  │ thumb  │  │ thumb  │                                │
│ │ date   │  │ date   │  │ date   │                                │
│ │ title  │  │ title  │  │ title  │                                │
│ └────────┘  └────────┘  └────────┘                                │
├────────────────────────────────────────────────────────────────────┤
│ FEATURED PRODUCTS                                 [Shop all →]     │
│ [prod] [prod] [prod] [prod]                                        │
├────────────────────────────────────────────────────────────────────┤
│                       BECOME A MEMBER                              │
│              Monthly ¥1,000  ·  Yearly ¥12,000                     │
│                          [ JOIN NOW ]                              │
├────────────────────────────────────────────────────────────────────┤
│ FOOTER (4 columns + SNS + ©)                                       │
└────────────────────────────────────────────────────────────────────┘
```

**主要要素**: ヒーロー（CTA）／NEWS 最新3件カード／注目商品 4枚／メンバーシップバナー／フッター

### 2.2 Profile `/pages/profile`  [→ `profile.html`](./profile.html)

```
┌────────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
├────────────────────────────────────────────────────────────────────┤
│ ┌────────────────────┐  FUMI                                       │
│ │                    │  Model · Actress                            │
│ │   [ PORTRAIT ]     │                                             │
│ │                    │  Birthday  : YYYY.MM.DD                     │
│ │                    │  Height    : --- cm                         │
│ │                    │  Hometown  : ---                            │
│ │                    │  SNS       : IG · YT · X                    │
│ └────────────────────┘                                             │
│                                                                    │
│                         BIOGRAPHY                                  │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │ Multi-paragraph biography text                             │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│                          CAREER                                    │
│   · 2024 — TV Drama "○○○"                                          │
│   · 2025 — Cover model, ○○○ Magazine                               │
├────────────────────────────────────────────────────────────────────┤
│ FILMOGRAPHY / WORKS                                                │
│ [work] [work] [work]                                               │
├────────────────────────────────────────────────────────────────────┤
│ FOOTER                                                             │
└────────────────────────────────────────────────────────────────────┘
```

### 2.3 News `/pages/news`

```
┌────────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
├────────────────────────────────────────────────────────────────────┤
│ NEWS                                                               │
│ Filter: [Year ▼] [Category ▼]                  Search: [        ]  │
├────────────────────────────────────────────────────────────────────┤
│ ┌──┐ 2026.04.20 · NEWS                                             │
│ │  │ News title — single line                              [→]    │
│ └──┘                                                               │
│ ┌──┐ 2026.04.15 · EVENT                                            │
│ │  │ News title — single line                              [→]    │
│ └──┘                                                               │
│ ┌──┐ 2026.04.01 · MEDIA                                            │
│ │  │ ...                                                            │
│ └──┘                                                               │
│ ...                                                                │
├────────────────────────────────────────────────────────────────────┤
│           « Prev   1  2  3  ...  Next »                            │
├────────────────────────────────────────────────────────────────────┤
│ FOOTER                                                             │
└────────────────────────────────────────────────────────────────────┘
```

**要素**: タイトル / カテゴリフィルタ / 年フィルタ / 検索 / 記事カード（縦積み）/ ページネーション

### 2.4 Shop / Collection `/pages/shop` → `/collections/all`  [→ `shop.html`](./shop.html)

```
┌────────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
├────────────────────────────────────────────────────────────────────┤
│ SHOP / ALL PRODUCTS                                                │
├────────────────────────────────────────────────────────────────────┤
│ [ALL] [PHOTOBOOK] [DVD] [GOODS] [MEMBERS ONLY]   Sort: [Newest ▼]  │
├────────────────────────────────────────────────────────────────────┤
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐                                       │
│ │img │ │img │ │img │ │img │                                       │
│ │name│ │name│ │name│ │name│                                       │
│ │¥   │ │¥   │ │¥   │ │¥   │                                       │
│ └────┘ └────┘ └────┘ └────┘                                       │
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐                                       │
│ │img │ │img │ │img │ │img │                                       │
│ └────┘ └────┘ └────┘ └────┘                                       │
├────────────────────────────────────────────────────────────────────┤
│           « Prev   [1]  2  3   Next »                              │
├────────────────────────────────────────────────────────────────────┤
│ FOOTER                                                             │
└────────────────────────────────────────────────────────────────────┘
```

**要素**: カテゴリタブ / 並び替えセレクト / 商品グリッド（4列）/ "MEMBERS" バッジ / ページネーション

### 2.5 Product Detail `/products/*`  [→ `product.html`](./product.html)

```
┌────────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
├────────────────────────────────────────────────────────────────────┤
│ Home / Shop / Photobook "Lumina"                                   │
├────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────┐    PHOTOBOOK                                  │
│ │                  │    Photobook "Lumina"                         │
│ │   MAIN IMAGE     │    FUMI 1st Photobook · KADOKAWA              │
│ │                  │    ¥4,500 (税込)                               │
│ └──────────────────┘    ● In stock                                 │
│ [thumb][thumb][thumb]                                              │
│                          Variant: [ Standard ▼ ]                   │
│                          Qty:     [ 1 ]                            │
│                                                                    │
│                          [ Add to Cart ]  [ Buy it Now ]           │
│                                                                    │
│                          ✦ Members 10% off                         │
├────────────────────────────────────────────────────────────────────┤
│ [DESCRIPTION] [SPECS] [SHIPPING] [NOTES]                           │
│ Body text...                                                       │
├────────────────────────────────────────────────────────────────────┤
│ RELATED PRODUCTS                                                   │
│ [prod] [prod] [prod] [prod]                                        │
├────────────────────────────────────────────────────────────────────┤
│ FOOTER                                                             │
└────────────────────────────────────────────────────────────────────┘
```

### 2.6 FAQ `/pages/faq`

```
┌────────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
├────────────────────────────────────────────────────────────────────┤
│ FAQ / Q&A                                                          │
│ Categories: [Membership] [Login] [Shipping] [Refund]               │
├────────────────────────────────────────────────────────────────────┤
│ ▸ How do I become a member?                                        │
│ ▾ I forgot my password — how do I reset it?                        │
│    Answer body text...                                             │
│ ▸ Do you ship internationally?                                     │
│ ▸ Can I get a refund?                                              │
├────────────────────────────────────────────────────────────────────┤
│ FOOTER                                                             │
└────────────────────────────────────────────────────────────────────┘
```

**要素**: カテゴリタブ / アコーディオン Q&A

### 2.7 Account: Login & Register `/account/login` `/account/register`

```
┌────────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│              ┌─────────────────────────────┐                       │
│              │  LOGIN                      │                       │
│              │  ─────────────────────────  │                       │
│              │  Email     [             ]  │                       │
│              │  Password  [             ]  │                       │
│              │             [ LOGIN ]       │                       │
│              │  Forgot password?           │                       │
│              │  ─────────────────────────  │                       │
│              │  Don't have an account?     │                       │
│              │  → Create account           │                       │
│              └─────────────────────────────┘                       │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│ FOOTER                                                             │
└────────────────────────────────────────────────────────────────────┘
```

Register 画面は同レイアウトで `Email / Password / Confirm Password / [Register]` ＋規約同意チェック。

### 2.8 静的ページ（About / Contact / Membership Agreement / Privacy Policy / 特商法）

すべて単一カラム、見出し ＋ 段組テキスト ＋ フッター。法務系ページ（特商法 / Privacy / 規約）は dl/dt/dd の定義リスト形式で項目構成。

```
┌────────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
├────────────────────────────────────────────────────────────────────┤
│ PAGE TITLE                                                         │
├────────────────────────────────────────────────────────────────────┤
│ Body text (single column, max 800px)                               │
│ ────────────────────────────────────────────                       │
│ [Section 1]                                                        │
│   Term : Definition                                                │
│   Term : Definition                                                │
│ ────────────────────────────────────────────                       │
│ [Section 2]                                                        │
│   ...                                                              │
├────────────────────────────────────────────────────────────────────┤
│ FOOTER                                                             │
└────────────────────────────────────────────────────────────────────┘
```

---

## 3. デザインメモ（実装時の指針）

| 項目 | 指針 |
|---|---|
| カラー | pyoeunji.com 同様にホワイト基調＋ダークアクセント。本人キービジュアル（写真）が主役。 |
| タイポグラフィ | 英大文字 + 文字間 0.1〜0.2em のレタースペーシングで「official」感。和文は明朝より角ゴシック寄り。 |
| 余白 | セクション間 48〜64px。グリッド左右パディング 24px。 |
| 画像 | ヒーローはフルブリード、商品はスクエア比 1:1、ニュースサムネは 16:9。 |
| インタラクション | カード hover 時にわずかにスケール／影。CTA は色反転 hover。 |

---

## 4. 検証方法

```bash
# wireframes ディレクトリ配下で簡易サーバを起動
python3 -m http.server 8000 --directory /home/user/fumi-site/wireframes

# ブラウザで以下を確認
#   http://localhost:8000/index.html      ← Home
#   http://localhost:8000/profile.html
#   http://localhost:8000/shop.html
#   http://localhost:8000/product.html
```

各ページのヘッダーリンクで相互遷移できることを確認する。

---

## 5. 設計判断ログ（弁証法）

| # | 論点 | 正 (Thesis) | 反 (Antithesis) | 合 (Synthesis) |
|---|---|---|---|---|
| 1 | 成果物形式 | Markdown のみ — 軽量だが視覚検証不可 | HTML のみ — 視覚的だが俯瞰性に欠ける | **MD（IA俯瞰）+ HTML 4枚（視覚検証）** の二層構造 |
| 2 | カバー範囲 | 全ページ — 完全だが冗長 | TOP のみ — 軽量だが IA が見えない | **コア7ページを MD、代表 4 ページを HTML 化** |
| 3 | コンセプト | pyoeunji 完全再現 — 純度は高いが repo 名と乖離 | 完全架空のプレースホルダー — 中立だが薄い | **「FUMI OFFICIAL FANCLUB」へリブランド・構造は pyoeunji.com を忠実踏襲** |

---

## 6. ファイル一覧

```
wireframes/
├── README.md           ← 本ドキュメント
├── assets/
│   └── wireframe.css   ← 共通の低忠実度スタイル
├── index.html          ← Home / CONTENT
├── profile.html        ← Profile
├── shop.html           ← Shop / Collection (all)
└── product.html        ← Product Detail
```

参考ソース:
- [PYO EUNJI OFFICIAL FANCLUB / Home](https://pyoeunji.com/en)
- [Profile](https://pyoeunji.com/en/pages/profile)
- [News](https://pyoeunji.com/en/pages/news)
- [FAQ](https://pyoeunji.com/en/pages/faq)
- [About](https://pyoeunji.com/en/pages/about)
- [Collections](https://pyoeunji.com/en/collections)
- [Login](https://pyoeunji.com/en/account/login)
- [Register](https://pyoeunji.com/en/account/register)
- [特商法 (SCC)](https://pyoeunji.com/en/pages/scc)
- [Privacy Policy](https://pyoeunji.com/en/pages/pp)
