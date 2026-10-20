# 🧠 第二の脳（FLEX-TENCHO SECOND BRAIN）

文章を貼って「保存」を押すだけ。AIが分類・要約してNotionへ。原文は絶対に消えません。

## 毎日の使い方（セットアップ後）
1. `起動.bat`（Macは `start.sh`）をダブルクリック
2. ブラウザで http://127.0.0.1:8765 を開く
3. 貼る → 保存（Ctrl+Enterでも可）

## 初回セットアップ（3アクション）
1. このフォルダを解凍する
2. Notionで連携(Integration)を作り、シークレットをコピー。親ページを1つ作り、連携を共有（『…』→『接続』）
3. `セットアップ.bat` をダブルクリック → 鍵とページURLを貼る。あとは全自動
   （AIは店内のOllama `gemma2:9b` を使うので、AI料金は0円）

困ったら：画面に「⚠️失敗」が出ても原文はPC内に保存済み。「再送」ボタンか `python -m app retry`。

詳しい設計は `docs/01_設計書_Phase1.md`。テスト：`python -m unittest discover -s tests -t .`
