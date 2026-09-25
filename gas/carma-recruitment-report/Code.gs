/**
 * SM.Carma 採用ログ自動分析・レポート生成
 *
 * セットアップ手順は README.md を参照。
 * 初回だけ initializeCarmaRecruitmentSystem() を手動実行すること。
 */

// ── 設定値 ──────────────────────────────────────────
var SHEET_LOG = '採用ログ';
var SHEET_REPORT = 'レポート';
var SHEET_CHECK = '検算_自動生成_編集不要';
var REPORT_EMAIL = 'fumi@carma.jp'; // Fumi-chan本人のみ。CC/BCCでの拡散は行わない。
var MEDIA_LIST = ['Ichigo Navi', 'Qpuri', 'LP直接応募'];
var MIN_SAMPLE_SIZE = 5;
var MINUTES_PER_REPLY = 15; // Fumi-chanの1件あたり平均対応時間（仮置き。判明次第この数値を更新すること）
var LOG_HEADERS = ['日付', '候補者名', '媒体', '開封', '返信', '面接', '結果'];

// ── セットアップ（初回のみ手動実行） ──────────────────────
function initializeCarmaRecruitmentSystem() {
  var props = PropertiesService.getScriptProperties();

  var ss = openOrCreateSpreadsheet_(props);
  ensureLogSheet_(ss);
  ensureReportSheet_(ss);
  ensureCheckSheet_(ss);

  var folder = openOrCreateReportsFolder_(props);

  installMonthlyTrigger_();

  var ownerEmail = Session.getActiveUser().getEmail() || Session.getEffectiveUser().getEmail();
  var message = [
    'SM.Carma 採用ログ自動分析システムのセットアップが完了しました。',
    '',
    'スプレッドシート: ' + ss.getUrl(),
    'CSV保存フォルダ（reports）: ' + folder.getUrl(),
    '',
    '「採用ログ」タブに日々の送信記録を追記してください（既存の行・列は削除しないこと）。',
    '毎月1日 朝8:00に、前月分のレポートが自動生成され「レポート」タブが更新されます。',
    '同時に ' + REPORT_EMAIL + ' 宛にメールでお知らせします。',
    '',
    '今すぐ動作確認したい場合は、この後 manualRunForTesting() を実行してください（今月のデータでレポートを試作します）。'
  ].join('\n');

  if (ownerEmail) {
    MailApp.sendEmail(ownerEmail, '【セットアップ完了】SM.Carma 採用レポート自動化', message);
  }
  Logger.log(message);
}

function openOrCreateSpreadsheet_(props) {
  var ssId = props.getProperty('SPREADSHEET_ID');
  if (ssId) {
    try {
      return SpreadsheetApp.openById(ssId);
    } catch (e) {
      // 保存されていたIDが無効な場合は作り直す
    }
  }
  var ss = SpreadsheetApp.create('SM.Carma 採用ログ・レポート');
  props.setProperty('SPREADSHEET_ID', ss.getId());
  return ss;
}

function openOrCreateReportsFolder_(props) {
  var folderId = props.getProperty('REPORTS_FOLDER_ID');
  if (folderId) {
    try {
      return DriveApp.getFolderById(folderId);
    } catch (e) {
      // 保存されていたIDが無効な場合は作り直す
    }
  }
  var folder = DriveApp.createFolder('reports');
  props.setProperty('REPORTS_FOLDER_ID', folder.getId());
  return folder;
}

function ensureLogSheet_(ss) {
  var sheet = ss.getSheetByName(SHEET_LOG);
  var isNew = !sheet;
  if (isNew) {
    sheet = ss.insertSheet(SHEET_LOG);
    sheet.getRange(1, 1, 1, LOG_HEADERS.length).setValues([LOG_HEADERS]);
    sheet.getRange(1, 1, 1, LOG_HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);

    var maxRows = 2000;
    sheet.getRange(2, 3, maxRows, 1).setDataValidation(
      SpreadsheetApp.newDataValidation().requireValueInList(MEDIA_LIST, true).build()
    );
    sheet.getRange(2, 4, maxRows, 2).insertCheckboxes(); // 開封・返信
    sheet.getRange(2, 6, maxRows, 1).setDataValidation(
      SpreadsheetApp.newDataValidation().requireValueInList(['実施済み', '未実施'], true).build()
    );
    sheet.getRange(2, 7, maxRows, 1).setDataValidation(
      SpreadsheetApp.newDataValidation().requireValueInList(['採用', '不採用', '選考中'], true).build()
    );
    sheet.autoResizeColumns(1, LOG_HEADERS.length);
  }
  // デフォルトシート（シート1）が残っていて空なら削除する
  var defaultSheet = ss.getSheetByName('シート1');
  if (defaultSheet && ss.getSheets().length > 1 && defaultSheet.getLastRow() === 0) {
    ss.deleteSheet(defaultSheet);
  }
  return sheet;
}

function ensureReportSheet_(ss) {
  var sheet = ss.getSheetByName(SHEET_REPORT);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_REPORT);
  }
  return sheet;
}

function ensureCheckSheet_(ss) {
  var sheet = ss.getSheetByName(SHEET_CHECK);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_CHECK);
  }
  return sheet;
}

function installMonthlyTrigger_() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'monthlyRecruitmentReport') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
  ScriptApp.newTrigger('monthlyRecruitmentReport')
    .timeBased()
    .onMonthDay(1)
    .atHour(8)
    .create();
}

// ── 実行エントリポイント ──────────────────────────────
function monthlyRecruitmentReport() {
  var now = new Date();
  var y = now.getFullYear();
  var m = now.getMonth(); // 0-indexed（今月）
  // 月初(1日)に実行される想定のため、対象は「前月」とする
  var targetYear = m === 0 ? y - 1 : y;
  var targetMonthIndex = m === 0 ? 11 : m - 1;
  runReportForMonth_(targetYear, targetMonthIndex);
}

// 動作確認用：セットアップ直後などに今月のデータで試作したい場合に手動実行する
function manualRunForTesting() {
  var now = new Date();
  runReportForMonth_(now.getFullYear(), now.getMonth());
}

// ── コアロジック ────────────────────────────────────
function runReportForMonth_(targetYear, targetMonthIndex) {
  try {
    var props = PropertiesService.getScriptProperties();
    var ssId = props.getProperty('SPREADSHEET_ID');
    if (!ssId) {
      throw new Error('SPREADSHEET_ID が未設定です。先に initializeCarmaRecruitmentSystem() を実行してください。');
    }
    var ss = SpreadsheetApp.openById(ssId);

    var logSheet = ss.getSheetByName(SHEET_LOG);
    if (!logSheet) {
      throw new Error('「採用ログ」シートが見つかりません。シート名が変更・削除されていないか確認してください。');
    }

    var reportSheet = ensureReportSheet_(ss);
    var rangeStart = new Date(targetYear, targetMonthIndex, 1);
    var rangeEnd = new Date(targetYear, targetMonthIndex + 1, 1);
    var lastRow = logSheet.getLastRow();

    if (lastRow < 2) {
      writeEmptyReport_(reportSheet, targetYear, targetMonthIndex);
      sendReportEmail_(ss, reportSheet, targetYear, targetMonthIndex, null);
      return;
    }

    var data = logSheet.getRange(2, 1, lastRow - 1, LOG_HEADERS.length).getValues();
    var monthRows = data.filter(function (row) {
      var d = row[0];
      return d instanceof Date && d >= rangeStart && d < rangeEnd;
    });

    if (monthRows.length === 0) {
      writeEmptyReport_(reportSheet, targetYear, targetMonthIndex);
      sendReportEmail_(ss, reportSheet, targetYear, targetMonthIndex, null);
      return;
    }

    var check = buildVerificationSheet_(ss, rangeStart, rangeEnd, lastRow);
    var reportData = computeReportData_(check.metrics, monthRows);

    writeReportSheet_(reportSheet, targetYear, targetMonthIndex, reportData, check.mismatch);

    var folder = openOrCreateReportsFolder_(props);
    var csvContent = buildCsv_(targetYear, targetMonthIndex, reportData, check.mismatch);
    var fileName = Utilities.formatString('%04d-%02d.csv', targetYear, targetMonthIndex + 1);
    saveCsvToDrive_(folder, fileName, csvContent);

    sendReportEmail_(ss, reportSheet, targetYear, targetMonthIndex, csvContent, fileName, check.mismatch);
  } catch (err) {
    notifyError_(err);
  }
}

// ── 二重チェック（SUMIFS/SUMPRODUCT系 と COUNTIFS系を独立計算して突合） ──
function buildVerificationSheet_(ss, rangeStart, rangeEnd, lastRow) {
  var sheet = ensureCheckSheet_(ss);
  sheet.clearContents();

  var y1 = rangeStart.getFullYear(), m1 = rangeStart.getMonth() + 1;
  var y2 = rangeEnd.getFullYear(), m2 = rangeEnd.getMonth() + 1;
  var n = lastRow;

  var dateRange = "'" + SHEET_LOG + "'!$A$2:$A$" + n;
  var mediaRange = "'" + SHEET_LOG + "'!$C$2:$C$" + n;
  var openRange = "'" + SHEET_LOG + "'!$D$2:$D$" + n;
  var replyRange = "'" + SHEET_LOG + "'!$E$2:$E$" + n;
  var interviewRange = "'" + SHEET_LOG + "'!$F$2:$F$" + n;
  var resultRange = "'" + SHEET_LOG + "'!$G$2:$G$" + n;

  var startCrit = '">="&DATE(' + y1 + ',' + m1 + ',1)';
  var endCrit = '"<"&DATE(' + y2 + ',' + m2 + ',1)';
  var dateGteExpr = dateRange + '>=DATE(' + y1 + ',' + m1 + ',1)';
  var dateLtExpr = dateRange + '<DATE(' + y2 + ',' + m2 + ',1)';

  var rows = [['指標', 'COUNTIFS系', 'SUMIFS_SUMPRODUCT系', '一致']];

  function addMetric(label, countifsFormula, sumFormula) {
    rows.push([label, countifsFormula, sumFormula, '']);
  }

  addMetric(
    '送信数_全体',
    '=COUNTIFS(' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ')',
    '=SUMPRODUCT((' + dateGteExpr + ')*(' + dateLtExpr + '))'
  );
  addMetric(
    '開封数_全体',
    '=COUNTIFS(' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ',' + openRange + ',TRUE)',
    '=SUMIFS(' + openRange + ',' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ')'
  );
  addMetric(
    '返信数_全体',
    '=COUNTIFS(' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ',' + replyRange + ',TRUE)',
    '=SUMIFS(' + replyRange + ',' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ')'
  );
  addMetric(
    '面接実施数_全体',
    '=COUNTIFS(' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ',' + interviewRange + ',"実施済み")',
    '=SUMPRODUCT((' + dateGteExpr + ')*(' + dateLtExpr + ')*(' + interviewRange + '="実施済み"))'
  );
  addMetric(
    '採用数_全体',
    '=COUNTIFS(' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ',' + resultRange + ',"採用")',
    '=SUMPRODUCT((' + dateGteExpr + ')*(' + dateLtExpr + ')*(' + resultRange + '="採用"))'
  );

  MEDIA_LIST.forEach(function (media) {
    var mediaCrit = '"' + media + '"';
    var mediaEqExpr = mediaRange + '=' + mediaCrit;
    addMetric(
      '送信数_' + media,
      '=COUNTIFS(' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ',' + mediaRange + ',' + mediaCrit + ')',
      '=SUMPRODUCT((' + dateGteExpr + ')*(' + dateLtExpr + ')*(' + mediaEqExpr + '))'
    );
    addMetric(
      '開封数_' + media,
      '=COUNTIFS(' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ',' + mediaRange + ',' + mediaCrit + ',' + openRange + ',TRUE)',
      '=SUMIFS(' + openRange + ',' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ',' + mediaRange + ',' + mediaCrit + ')'
    );
    addMetric(
      '返信数_' + media,
      '=COUNTIFS(' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ',' + mediaRange + ',' + mediaCrit + ',' + replyRange + ',TRUE)',
      '=SUMIFS(' + replyRange + ',' + dateRange + ',' + startCrit + ',' + dateRange + ',' + endCrit + ',' + mediaRange + ',' + mediaCrit + ')'
    );
  });

  sheet.getRange(1, 1, rows.length, 4).setValues(rows);
  for (var i = 2; i <= rows.length; i++) {
    sheet.getRange(i, 4).setFormula('=B' + i + '=C' + i);
  }
  sheet.hideSheet();
  SpreadsheetApp.flush();

  var values = sheet.getRange(2, 1, rows.length - 1, 4).getValues();
  var metrics = {};
  var mismatch = false;
  values.forEach(function (r) {
    metrics[r[0]] = { countifs: r[1], sumifs: r[2], match: r[3] };
    if (r[3] !== true) mismatch = true;
  });
  return { metrics: metrics, mismatch: mismatch };
}

// ── 指標計算（二重チェック済みの件数から比率・提案を組み立てる） ──
function computeReportData_(metrics, monthRows) {
  var total = metrics['送信数_全体'].countifs;
  var opened = metrics['開封数_全体'].countifs;
  var replied = metrics['返信数_全体'].countifs;
  var interviewed = metrics['面接実施数_全体'].countifs;
  var hired = metrics['採用数_全体'].countifs;

  var openRate = safeRate_(opened, total, 'データなし');
  var replyRate = safeRate_(replied, opened, 'データなし');
  var interviewRate = safeRate_(interviewed, replied, 'データなし');
  var hireRate = safeRate_(hired, interviewed, '実施なし');

  var mediaStats = MEDIA_LIST.map(function (media) {
    var mTotal = metrics['送信数_' + media].countifs;
    var mOpened = metrics['開封数_' + media].countifs;
    var mReplied = metrics['返信数_' + media].countifs;
    return {
      media: media,
      total: mTotal,
      opened: mOpened,
      replied: mReplied,
      openRate: safeRate_(mOpened, mTotal, 'データなし'),
      replyRate: safeRate_(mReplied, mOpened, 'データなし'),
      lowSample: mTotal < MIN_SAMPLE_SIZE
    };
  });

  var suggestions = buildSuggestions_(mediaStats, {
    total: total, opened: opened, replied: replied, interviewed: interviewed, hired: hired,
    openRate: openRate, replyRate: replyRate, interviewRate: interviewRate, hireRate: hireRate
  });

  var fumiMinutes = replied * MINUTES_PER_REPLY;

  return {
    total: total, opened: opened, replied: replied, interviewed: interviewed, hired: hired,
    openRate: openRate, replyRate: replyRate, interviewRate: interviewRate, hireRate: hireRate,
    mediaStats: mediaStats,
    suggestions: suggestions,
    fumiMinutes: fumiMinutes
  };
}

function safeRate_(numerator, denominator, zeroLabel) {
  if (!denominator) return zeroLabel;
  return (numerator / denominator * 100).toFixed(1) + '%';
}

// データに基づく場合のみ提案を採用する。根拠のない一般論は入れない。
function buildSuggestions_(mediaStats, overall) {
  var suggestions = [];
  var validMedia = mediaStats.filter(function (m) { return !m.lowSample && m.opened > 0; });

  if (validMedia.length >= 2) {
    var sorted = validMedia.slice().sort(function (a, b) {
      return (b.replied / b.opened) - (a.replied / a.opened);
    });
    var best = sorted[0], worst = sorted[sorted.length - 1];
    var bestRate = (best.replied / best.opened * 100);
    var worstRate = (worst.replied / worst.opened * 100);
    if (bestRate - worstRate >= 10) {
      suggestions.push(
        best.media + 'の返信率が' + bestRate.toFixed(1) + '%と、' + worst.media + '（' + worstRate.toFixed(1) + '%）より' +
        (bestRate - worstRate).toFixed(1) + 'pt高い。送信数の配分を' + best.media + '側に寄せる価値がある。'
      );
    }
  }

  if (overall.replied >= 3 && overall.interviewed / overall.replied < 0.5) {
    suggestions.push(
      '返信' + overall.replied + '件に対して面接実施は' + overall.interviewed + '件（' + overall.interviewRate +
      '）にとどまる。返信後のフォロー速度・日程調整の導線を見直す余地あり。'
    );
  }

  if (overall.interviewed >= 2 && overall.hired / overall.interviewed >= 0.5) {
    suggestions.push(
      '面接実施' + overall.interviewed + '件のうち採用' + overall.hired + '件（' + overall.hireRate +
      '）と成約率が高い。面接まで進める母数を増やせば採用数の増加が見込める。'
    );
  }

  mediaStats.forEach(function (m) {
    if (m.lowSample && m.total > 0 && suggestions.length < 3) {
      suggestions.push(
        m.media + 'は送信数' + m.total + '件とサンプル数が少なく、優劣判定はまだ出せない。次月以降データを積み増して判断する。'
      );
    }
  });

  return suggestions.slice(0, 3);
}

// ── レポート出力 ────────────────────────────────────
function writeReportSheet_(sheet, year, monthIndex, d, mismatch) {
  sheet.clear();
  var monthLabel = year + '年' + (monthIndex + 1) + '月度';
  var rows = [];

  if (mismatch) {
    rows.push(['⚠ 計算不一致あり：要手動確認（「' + SHEET_CHECK + '」シート参照）']);
    rows.push(['']);
  }

  rows.push(['SM.Carma 採用レポート　' + monthLabel]);
  rows.push(['生成日時', Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm')]);
  rows.push(['']);

  rows.push(['■ 今月の応募者総数（送信数）', d.total + '件']);
  rows.push(['']);

  rows.push(['■ 媒体別 開封率・返信率']);
  rows.push(['媒体', '送信数', '開封率', '返信率', '備考']);
  d.mediaStats.forEach(function (m) {
    rows.push([m.media, m.total, m.openRate, m.replyRate, m.lowSample ? 'サンプル数不足' : '']);
  });
  rows.push(['']);

  rows.push(['■ 面接→採用の確度']);
  rows.push(['面接実施率（返信→面接）', d.interviewRate]);
  rows.push(['採用確度（面接→採用）', d.hireRate]);
  rows.push(['']);

  rows.push(['■ Ichigo Navi vs Qpuri 効率比較（返信率）']);
  var ichigo = d.mediaStats.filter(function (m) { return m.media === 'Ichigo Navi'; })[0];
  var qpuri = d.mediaStats.filter(function (m) { return m.media === 'Qpuri'; })[0];
  if (ichigo.lowSample || qpuri.lowSample) {
    rows.push(['どちらか、または両方がサンプル数不足のため、断定的な優劣判定はしない。']);
    rows.push(['Ichigo Navi', ichigo.total + '件 / 返信率 ' + ichigo.replyRate]);
    rows.push(['Qpuri', qpuri.total + '件 / 返信率 ' + qpuri.replyRate]);
  } else {
    rows.push(['Ichigo Navi', ichigo.total + '件 / 返信率 ' + ichigo.replyRate]);
    rows.push(['Qpuri', qpuri.total + '件 / 返信率 ' + qpuri.replyRate]);
  }
  rows.push(['']);

  rows.push(['■ 改善提案']);
  if (d.suggestions.length === 0) {
    rows.push(['（今月のデータからは断定できる提案なし）']);
  } else {
    d.suggestions.forEach(function (s, idx) {
      rows.push([(idx + 1) + '. ' + s]);
    });
  }
  rows.push(['']);

  rows.push(['■ Fumi-chan 手作業工数推定']);
  rows.push(['返信数 × 1件あたり' + MINUTES_PER_REPLY + '分', d.fumiMinutes + '分（約' + (d.fumiMinutes / 60).toFixed(1) + '時間）']);

  var maxCols = rows.reduce(function (max, r) { return Math.max(max, r.length); }, 1);
  var padded = rows.map(function (r) {
    var copy = r.slice();
    while (copy.length < maxCols) copy.push('');
    return copy;
  });
  sheet.getRange(1, 1, padded.length, maxCols).setValues(padded);

  // 見出し行を太字にする
  padded.forEach(function (r, idx) {
    if (typeof r[0] === 'string' && (r[0].indexOf('■') === 0 || r[0].indexOf('⚠') === 0 || r[0] === 'SM.Carma 採用レポート　' + monthLabel)) {
      sheet.getRange(idx + 1, 1).setFontWeight('bold');
    }
  });
  sheet.autoResizeColumns(1, maxCols);
}

function writeEmptyReport_(sheet, year, monthIndex) {
  sheet.clear();
  var monthLabel = year + '年' + (monthIndex + 1) + '月度';
  sheet.getRange(1, 1, 3, 1).setValues([
    ['SM.Carma 採用レポート　' + monthLabel],
    ['生成日時: ' + Utilities.formatDate(new Date(), 'Asia/Tokyo', 'yyyy-MM-dd HH:mm')],
    ['対象月はデータなし']
  ]);
  sheet.getRange(1, 1).setFontWeight('bold');
  sheet.autoResizeColumns(1, 1);
}

// ── CSV出力 ────────────────────────────────────────
function buildCsv_(year, monthIndex, d, mismatch) {
  var lines = [];
  if (mismatch) lines.push('⚠ 計算不一致あり：要手動確認');
  lines.push('SM.Carma 採用レポート,' + year + '年' + (monthIndex + 1) + '月度');
  lines.push('送信数,' + d.total);
  lines.push('');
  lines.push('媒体,送信数,開封率,返信率,備考');
  d.mediaStats.forEach(function (m) {
    lines.push([m.media, m.total, m.openRate, m.replyRate, m.lowSample ? 'サンプル数不足' : ''].join(','));
  });
  lines.push('');
  lines.push('面接実施率,' + d.interviewRate);
  lines.push('採用確度,' + d.hireRate);
  lines.push('');
  lines.push('改善提案');
  d.suggestions.forEach(function (s, idx) {
    lines.push((idx + 1) + '. ' + csvEscape_(s));
  });
  lines.push('');
  lines.push('Fumi-chan手作業工数推定(分),' + d.fumiMinutes);
  return lines.join('\n');
}

function csvEscape_(text) {
  if (text.indexOf(',') === -1 && text.indexOf('"') === -1) return text;
  return '"' + text.replace(/"/g, '""') + '"';
}

function saveCsvToDrive_(folder, fileName, csvContent) {
  var existing = folder.getFilesByName(fileName);
  while (existing.hasNext()) {
    existing.next().setTrashed(true);
  }
  folder.createFile(fileName, csvContent, MimeType.CSV);
}

// ── メール送信 ──────────────────────────────────────
function sendReportEmail_(ss, reportSheet, year, monthIndex, csvContent, fileName, mismatch) {
  var monthLabel = year + '年' + (monthIndex + 1) + '月度';
  var url = ss.getUrl() + '#gid=' + reportSheet.getSheetId();
  var subject = (mismatch ? '【要確認】' : '【SM.Carma】') + monthLabel + ' 採用レポート';
  var bodyLines = [
    monthLabel + 'の採用レポートを更新しました。',
    '',
    'レポートはこちら: ' + url
  ];
  if (mismatch) {
    bodyLines.push('', '⚠ 集計に不一致があります。「' + SHEET_CHECK + '」シートで手動確認をお願いします。');
  }
  var options = {};
  if (csvContent && fileName) {
    options.attachments = [Utilities.newBlob(csvContent, MimeType.CSV, fileName)];
  }
  MailApp.sendEmail(REPORT_EMAIL, subject, bodyLines.join('\n'), options);
}

// ── エラー通知 ──────────────────────────────────────
function notifyError_(err) {
  var subject = '【エラー】SM.Carma 採用レポート自動生成に失敗しました';
  var body = 'レポート生成中にエラーが発生しました。\n\n内容: ' + err.message + '\n\n' + (err.stack || '');
  MailApp.sendEmail(REPORT_EMAIL, subject, body);
  Logger.log(body);
}
