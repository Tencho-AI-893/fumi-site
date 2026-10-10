#!/usr/bin/env python3
"""売上日報ツール（標準機能のみ）。実行: python nippo.py"""

import csv
import os
from datetime import date, datetime, timedelta

OUT_DIR = "nippo"
CSV_NAME = "売上記録.csv"
HEADER = ["日付", "来店組数", "来店数", "売上合計", "現金", "カード", "その他",
          "組単価", "客単価", "平均人数", "コメント"]


# ---------- 入力まわり ----------
def ask_date():
    while True:
        s = input("日付（Enterで今日 / 例 2026-10-10）: ").strip()
        if not s:
            return date.today()
        s = s.replace("/", "-").replace(".", "-")
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            print("  ※ 日付の形が違うようです。例: 2026-10-10 の形で入れてください。")


def ask_int(label, minimum=0):
    while True:
        s = input(f"{label}: ").strip().replace(",", "").replace("，", "").replace("円", "")
        s = s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
        try:
            n = int(s)
        except ValueError:
            print("  ※ 数字だけで入れてください（例: 350000）。")
            continue
        if n < minimum:
            print(f"  ※ {minimum}以上の数字を入れてください。")
            continue
        return n


def ask_yes(question):
    while True:
        s = input(f"{question} (y/n): ").strip().lower()
        if s in ("y", "yes", "はい", "ｙ"):
            return True
        if s in ("n", "no", "いいえ", "ｎ"):
            return False
        print("  ※ y か n で答えてください。")


def yen(n):
    return f"{n:,}円"


def safe_div(a, b):
    return round(a / b) if b else 0


# ---------- 記録の読み書き ----------
def csv_path():
    return os.path.join(OUT_DIR, CSV_NAME)


def load_records():
    """CSVから過去の記録を {日付文字列: 行dict} で返す。"""
    path = csv_path()
    if not os.path.exists(path):
        return {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        return {row["日付"]: row for row in csv.DictReader(f) if row.get("日付")}


def save_records(records):
    """日付順に並べてCSV全体を書き直す（UTF-8 BOM付き）。"""
    with open(csv_path(), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        for k in sorted(records):
            w.writerow(records[k])


# ---------- 日報の組み立て ----------
def build_report(d, r, records):
    sales = int(r["売上合計"])
    key = d.isoformat()

    # 前日比
    prev = records.get((d - timedelta(days=1)).isoformat())
    if prev and int(prev["売上合計"]) > 0:
        p = int(prev["売上合計"])
        pct = (sales - p) / p * 100
        mark = "▲" if pct < 0 else "＋"
        zenjitsu = f"{mark}{abs(pct):.1f}%（前日 {yen(p)}）"
    else:
        zenjitsu = "前日データなし"

    # 今月累計（その月の1日〜この日まで）
    ym = key[:7]
    month = [int(v["売上合計"]) for k, v in records.items() if k[:7] == ym and k <= key]
    total = sum(month)
    days = len(month)

    wd = "月火水木金土日"[d.weekday()]
    lines = [
        f"【売上日報】{d.year}年{d.month}月{d.day}日（{wd}）",
        "",
        "■ 売上サマリー",
        f"売上合計：{yen(sales)}",
        f"前日比：{zenjitsu}",
        f"来店：{r['来店組数']}組 / {r['来店数']}名（1組平均 {float(r['平均人数']):.1f}名）",
        f"組単価：{yen(int(r['組単価']))} / 客単価：{yen(int(r['客単価']))}",
        f"今月累計：{yen(total)}（{days}日営業・1日平均 {yen(safe_div(total, days))}）",
        "",
        "■ 内訳",
        f"現金：{yen(int(r['現金']))}",
        f"カード：{yen(int(r['カード']))}",
        f"その他：{yen(int(r['その他']))}",
    ]
    if r["コメント"]:
        lines += ["", "■ 本日のコメント", r["コメント"]]
    return "\n".join(lines) + "\n"


# ---------- メイン ----------
def main():
    print("=== 売上日報ツール ===（途中でやめる時は Ctrl+C）\n")
    os.makedirs(OUT_DIR, exist_ok=True)
    records = load_records()

    d = ask_date()
    key = d.isoformat()
    if key in records:
        if not ask_yes(f"{key} の日報はすでにあります。上書きしますか？"):
            print("保存せずに終了しました。")
            return

    groups = ask_int("来店組数（組）")
    sales = ask_int("売上合計（円）")
    cash = ask_int("  現金（円）")
    card = ask_int("  カード（円）")
    other = ask_int("  その他（円）")
    guests = ask_int("来店数（お客さんの総人数）")
    comment = input("本日のコメント（なければEnter）: ").strip().replace("\r", " ").replace("\n", " ")

    diff = sales - (cash + card + other)
    if diff != 0:
        if not ask_yes(f"差額が{abs(diff):,}円あります（売上合計 {yen(sales)} / 内訳合計 {yen(cash + card + other)}）。"
                       "このまま保存しますか？"):
            print("保存せずに終了しました。もう一度やり直してください。")
            return

    row = {
        "日付": key, "来店組数": groups, "来店数": guests, "売上合計": sales,
        "現金": cash, "カード": card, "その他": other,
        "組単価": safe_div(sales, groups), "客単価": safe_div(sales, guests),
        "平均人数": f"{guests / groups:.2f}" if groups else "0.00",
        "コメント": comment,
    }
    records[key] = row
    save_records(records)

    report = build_report(d, row, records)
    md_path = os.path.join(OUT_DIR, f"{key}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(report)

    print("\n" + "-" * 30)
    print(report)
    print("-" * 30)
    print(f"保存しました: {md_path} と {csv_path()}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n中断しました（何も保存されていません）。")
