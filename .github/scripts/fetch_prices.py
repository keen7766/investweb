"""investWEB: bütün səhmlərin qiymətini Yahoo Finance-dən çəkib stocks.json-a yazır.

GitHub Actions hər ~5 dəqiqədən bir işə salır. Proqram bu faylı oxuyur ki,
Finnhub açarı olmadan da bütün səhmlərdə qiymət görünsün.
İstifadə: python fetch_prices.py index.html stocks.json
"""
import json
import re
import sys
import time
import urllib.request

page, out = sys.argv[1], sys.argv[2]
src = open(page, encoding="utf-8").read()
block = re.search(r"const UNIVERSE_SRC = \{(.*?)\n\};", src, re.S).group(1)
tickers = sorted(set(re.findall(r"([A-Z][A-Z.\-]*):\d+", block)))

quotes = {}
for i in range(0, len(tickers), 20):
    chunk = tickers[i:i + 20]
    url = "https://query1.finance.yahoo.com/v8/finance/spark?range=1d&interval=1d&symbols=" + ",".join(chunk)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (investWEB price bot)"})
            data = json.load(urllib.request.urlopen(req, timeout=25))
            break
        except Exception as e:  # müvəqqəti xəta: bir az gözləyib yenidən
            print("xəta", chunk[0], e)
            time.sleep(3 * (attempt + 1))
    else:
        continue
    for t in chunk:
        v = data.get(t) or {}
        close = [c for c in (v.get("close") or []) if c]
        prev = v.get("chartPreviousClose")
        if close and prev:
            quotes[t] = [round(close[-1], 4), round(prev, 4), None, None]
    time.sleep(0.4)

print(f"{len(quotes)}/{len(tickers)} səhm")
if len(quotes) < len(tickers) * 0.5:
    sys.exit("Çox az qiymət gəldi, fayl yenilənmədi")
json.dump({"updated": int(time.time()), "quotes": quotes}, open(out, "w"), separators=(",", ":"))
