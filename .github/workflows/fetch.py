import requests
import csv
import os
from datetime import datetime, timezone, timedelta

MEMBERS = {
    "YOUNGSEO": {"param_id": "11734726", "initial_stock": 10000},
    "ANNIE": {"param_id": "11734722", "initial_stock": 10000},
    "TARZZAN": {"param_id": "11734723", "initial_stock": 10000},
    "BAILEY": {"param_id": "11734724", "initial_stock": 10000},
    "WOOCHAN": {"param_id": "11734725", "initial_stock": 10000},
}

URL = "https://www.imini.tv/mallorder/api/detail.php"
PRO_ID = "59374202"
CSV_PATH = "imini_sales.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.6.1 Safari/605.1.15",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"https://www.imini.tv/xingjunwenhua/wap_pro/{PRO_ID}.html"
}

def fetch_member(member_name, param_id):
    payload = {
        "username": "xingjunwenhua",
        "pro_id": PRO_ID,
        "param_id": param_id,
        "regionCode": "",
        "vue_cur_page_url": f"https://www.imini.tv/xingjunwenhua/wap_pro/{PRO_ID}.html"
    }
    try:
        r = requests.post(URL, headers=HEADERS, data=payload, timeout=15)
        r.raise_for_status()
        data = r.json()
        if data.get("code") == "200":
            return int(data["data"]["pro_stock"])
    except Exception as e:
        print(f"[ERROR] {member_name}: {e}")
    return None

def main():
    tw = timezone(timedelta(hours=8))
    now = datetime.now(tw).strftime("%Y-%m-%d %H:%M:%S")
    
    prev_stocks = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
            if len(lines) > 1:
                for line in reversed(lines[1:]):
                    parts = line.strip().split(",")
                    if len(parts) >= 4:
                        name = parts[1]
                        if name not in prev_stocks:
                            prev_stocks[name] = int(parts[3])
                    if len(prev_stocks) == len(MEMBERS):
                        break

    new_rows = []
    for name, info in MEMBERS.items():
        current_stock = fetch_member(name, info["param_id"])
        if current_stock is not None:
            sold_total = info["initial_stock"] - current_stock
            prev_stock = prev_stocks.get(name)
            
            delta = 0
            if prev_stock is not None and prev_stock > current_stock:
                delta = prev_stock - current_stock
                
            new_rows.append({
                "time": now,
                "member": name,
                "total_sold": sold_total,
                "stock": current_stock,
                "delta": delta
            })
            print(f"Success: {name} | 庫存: {current_stock} | 總銷量: {sold_total} | 增加: {delta}")

    if not new_rows:
        return

    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["time", "member", "total_sold", "stock", "delta"])
        if new_file:
            w.writeheader()
        w.writerows(new_rows)

if __name__ == "__main__":
    main()
