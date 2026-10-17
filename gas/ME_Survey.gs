/**
 * 会員データ拡張：1章 調査専用スクリプト（読み取りのみ）
 * - 書き込み・シート追加・メール送信・共有変更は一切しない
 * - 氏名・電話番号の中身は出力しない（見出し・行数・埋まり率のみ）
 * - 既存コードと関数名が衝突しないよう、すべて ME_ で始める
 * - onOpen は定義しない（既存の onOpen を上書きしないため）
 *
 * 使い方：Apps Script 画面で関数「ME_survey」を選んで「実行」→「実行ログ」をコピーして貼る
 */
const ME_SPREADSHEET_ID = '1_9QzQDCWfGCrc7erfYMKo8zQhm1kypl_ysTR65MegcUw';

function ME_survey() {
  const ss = SpreadsheetApp.openById(ME_SPREADSHEET_ID);
  const out = [];
  out.push('■ スプレッドシート名: ' + ss.getName());

  ss.getSheets().forEach(function (sh) {
    const lastRow = sh.getLastRow();
    const lastCol = sh.getLastColumn();
    out.push('');
    out.push('■ シート「' + sh.getName() + '」 行数(見出し含む)=' + lastRow + ' / 列数=' + lastCol +
             ' / 保護範囲=' + sh.getProtections(SpreadsheetApp.ProtectionType.RANGE).length +
             ' / 非表示=' + sh.isSheetHidden());
    if (lastRow < 1 || lastCol < 1) return;

    const headers = sh.getRange(1, 1, 1, lastCol).getValues()[0];
    const body = lastRow > 1 ? sh.getRange(2, 1, lastRow - 1, lastCol).getValues() : [];
    headers.forEach(function (h, i) {
      const col = i + 1;
      let filled = 0;
      body.forEach(function (r) { if (String(r[i]).trim() !== '') filled++; });
      const pct = body.length ? Math.round(filled * 100 / body.length) : 0;
      const hasValidation = lastRow > 1 && sh.getRange(2, col).getDataValidation() !== null;
      out.push('  列' + col + ' (' + ME_colLetter_(col) + ') 「' + h + '」 埋まり率=' + pct + '%' +
               (hasValidation ? ' [プルダウン等あり]' : ''));
    });
  });

  out.push('');
  out.push('■ 既存の自動実行トリガー数: ' + ScriptApp.getProjectTriggers().length);
  ScriptApp.getProjectTriggers().forEach(function (t) {
    out.push('  ' + t.getHandlerFunction() + ' / ' + t.getEventType());
  });

  Logger.log(out.join('\n'));
}

function ME_colLetter_(n) {
  let s = '';
  while (n > 0) { const m = (n - 1) % 26; s = String.fromCharCode(65 + m) + s; n = Math.floor((n - 1) / 26); }
  return s;
}
