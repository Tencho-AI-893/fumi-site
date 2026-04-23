# pyoeunji.com 分析 & FUMI サイト ワイヤーフレーム

## 1. 概要
本ドキュメントは、pyoeunji.com の情報設計（IA）をベースとし、架空の「FUMI OFFICIAL FANCLUB」のワイヤーフレーム構造を記述・解説したものです。

**弁証法による設計判断**
* 成果物フォーマット：`wireframes/README.md` による俯瞰性（正）と視覚確認・実装の土台としてのHTML提供（反）を組み合わせた**MD＋HTML二層構造**（合）
* 対象ページ範囲：全ページ（正）とTOPのみ（反）の中庸である**コア７ページMD定義＋代表４ページHTMLモック**（合）
* コンセプト：オリジナル再現実装（正）と完全架空（反）のバランスとして**「FUMI OFFICIAL FANCLUB」へのリブランド設定でのIA忠実再現**（合）

## 2. サイト情報構造（Information Architecture）
* pyoeunji.com と同様に、Shopify ベースを想定した EC＋コンテンツの統合型。

```
ROOT
├─ CONTENT（Home）          ヒーロー・最新ニュース・最新商品・会員CTA
├─ PROFILE                   本人プロフィール・実績
├─ NEWS                      記事リスト（ページネーション）
├─ SHOP                      → Collections
│   ├─ Collections           商品カテゴリ一覧
│   ├─ Products (All)        全商品グリッド
│   └─ Product Detail        単品ページ
├─ Account
│   ├─ Login
│   └─ Register
└─ Footer
    ├─ ABOUT
    ├─ CONTACT
    ├─ FAQ/Q&A
    ├─ MEMBERSHIP AGREEMENT
    ├─ PRIVACY POLICY
    └─ SCC 特商法
```

## 3. ページワイヤーフレーム（ASCII）

### 3.1 Home / CONTENT (`index.html`)
```
┌───────────────────────────────────────────────────┐
│ LOGO    CONTENT  PROFILE  SHOP  NEWS   JP/EN  LOGIN  [JOIN]│
├───────────────────────────────────────────────────┤
│                                                   │
│   [ HERO VISUAL — large portrait / key image ]    │
│        FUMI OFFICIAL FANCLUB                      │
│        [ BECOME A MEMBER ]                        │
│                                                   │
├───────────────────────────────────────────────────┤
│  NEWS (latest 3)                    [View all →] │
│  ┌────┐ ┌────┐ ┌────┐                             │
│  │img │ │img │ │img │                             │
│  │date│ │date│ │date│                             │
│  │ttl │ │ttl │ │ttl │                             │
│  └────┘ └────┘ └────┘                             │
├───────────────────────────────────────────────────┤
│  FEATURED PRODUCTS                  [Shop all →] │
│  [prod] [prod] [prod] [prod]                     │
├───────────────────────────────────────────────────┤
│  MEMBERSHIP BANNER                               │
│   Monthly ¥1,000 / Yearly ¥12,000                │
│   [ JOIN NOW ]                                    │
├───────────────────────────────────────────────────┤
│ FOOTER (Contact/About/Agreement/PP/特商法/FAQ + SNS) │
└───────────────────────────────────────────────────┘
```

### 3.2 Profile (`profile.html`)
```
┌───────────────────────────────────────────────────┐
│ LOGO    CONTENT  PROFILE  SHOP  NEWS   JP/EN  LOGIN  [JOIN]│
├───────────────────────────────────────────────────┤
│                                                   │
│  [ Portrait Image ]   NAME: FUMI                  │
│  [ (left side)    ]   BIRTH: 20XX.XX.XX           │
│  [                ]   HEIGHT: XXXcm               │
│  [                ]   DEBUT: 20XX                 │
│  [                ]   SNS Links: [Ig] [YT] [X]    │
│                                                   │
├───────────────────────────────────────────────────┤
│  BIOGRAPHY                                        │
│  Lorem ipsum dolor sit amet...                    │
│                                                   │
│  CAREER                                           │
│  - 202X: Event ABC                                │
│                                                   │
│  FILMOGRAPHY                                      │
│  - 202X: Movie DEF                                │
├───────────────────────────────────────────────────┤
│ FOOTER                                            │
└───────────────────────────────────────────────────┘
```

### 3.3 Shop/Collection (`shop.html`)
```
┌───────────────────────────────────────────────────┐
│ LOGO    CONTENT  PROFILE  SHOP  NEWS   JP/EN  LOGIN  [JOIN]│
├───────────────────────────────────────────────────┤
│  Categories: All / Photobook / DVD / Goods / M.O.  │
│  Sort by: [ Newest v ]                             │
├───────────────────────────────────────────────────┤
│  [img]         [img]         [img]         [img]  │
│  Product A     Product B     Product C     Product│
│  ¥2,000        ¥3,500        ¥1,000        ¥4,000 │
│                *Members Only                      │
├───────────────────────────────────────────────────┤
│ FOOTER                                            │
└───────────────────────────────────────────────────┘
```

### 3.4 Product Detail (`product.html`)
```
┌───────────────────────────────────────────────────┐
│ LOGO    CONTENT  PROFILE  SHOP  NEWS   JP/EN  LOGIN  [JOIN]│
├───────────────────────────────────────────────────┤
│  < Back to Shop                                   │
│                                                   │
│  [ Main Product ]    Title: Product Name          │
│  [   Image      ]    Price: ¥2,000                │
│  [              ]    Variant: [ Select v ]        │
│  [thumb][thumb]      Quantity: [ - 1 + ]          │
│                      [ Add to cart ] [ Buy it now]│
├───────────────────────────────────────────────────┤
│  Description:                                     │
│  Product specifications and details...            │
│  Notes / Shipping Info...                         │
├───────────────────────────────────────────────────┤
│ FOOTER                                            │
└───────────────────────────────────────────────────┘
```

### 3.5 News (`news.html` / MD Only)
```
┌───────────────────────────────────────────────────┐
│ LOGO    CONTENT  PROFILE  SHOP  NEWS   JP/EN  LOGIN  [JOIN]│
├───────────────────────────────────────────────────┤
│  NEWS                                             │
│  Filter: [ 2023 v ] [ Category v ]                │
│                                                   │
│  [img] 2023.10.01 - Category - News Title A       │
│  [img] 2023.09.15 - Category - News Title B       │
│                                                   │
│  < 1 2 3 >                                        │
├───────────────────────────────────────────────────┤
│ FOOTER                                            │
└───────────────────────────────────────────────────┘
```

### 3.6 FAQ (`faq.html` / MD Only)
* アコーディオン形式 Q&A（Membership / Login / Shipping / Refund）

### 3.7 Account: Login & Register (`login.html` / MD Only)
* 中央 1 カラム、`Email` / `Password` / `[Login]` / `Forgot password?` / `Create account →`

### 3.8 下位ページ群（MD Only）
* About / Contact / Membership Agreement / Privacy Policy / 特商法
* いずれも「タイトル + 本文一段組 + フッター」の静的テキストページ構成
