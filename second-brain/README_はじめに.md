# 🧠 第二の脳（FLEX-TENCHO SECOND BRAIN）

文章を貼って「保存」を押すだけ。AIが分類・要約してNotionへ。原文は絶対に消えません。

## 毎日の使い方（セットアップ後）
1. `起動.bat`（Macは `start.sh`）をダブルクリック
2. ブラウザで http://127.0.0.1:8765 を開く
3. 貼る → 保存（Ctrl+Enterでも可）

## 初回セットアップ（ここから1つずつ。次の手順は、前が終わってから案内します）
- Step 1：このPCにPythonが入っているか確認（`python --version`）
- Step 2：Notionで鍵(Integration)を作る
- Step 3：Notionに親ページを作って共有 → `python -m app setup <ページID>`
- Step 4：OpenAIのAPIキーを作る（課金の設定が必要。上限額も設定）
- Step 5：`.env.example` を `.env` にコピーして鍵を貼る → `python -m app check`
- Step 6：入力画面で1文だけ入れて、Notionに出れば成功 🎉

困ったら：画面に「⚠️失敗」が出ても原文はPC内に保存済み。「再送」ボタンか `python -m app retry`。

詳しい設計は `docs/01_設計書_Phase1.md`。テスト：`python -m unittest discover -s tests -t .`
