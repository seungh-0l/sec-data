import json, os, time, urllib.request

UA = os.environ["SEC_USER_AGENT"]          # 예: "Seungheon Kim your@email.com"

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r:
        return json.load(r)

# 티커 -> CIK 대응표 (SEC 제공)
table = get_json("https://www.sec.gov/files/company_tickers.json")
ticker_to_cik = {v["ticker"].upper(): v["cik_str"] for v in table.values()}

tickers = json.load(open("companies.json"))
os.makedirs("data", exist_ok=True)

for ticker in tickers:
    ticker = ticker.upper()
    cik = ticker_to_cik.get(ticker)
    if cik is None:
        print(f"skip {ticker}: CIK not found")
        continue
    cik10 = str(cik).zfill(10)
    targets = {
        "facts":   f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json",  # 재무 수치(XBRL)
        "filings": f"https://data.sec.gov/submissions/CIK{cik10}.json",            # 공시 목록
    }
    for kind, url in targets.items():
        try:
            data = get_json(url)
        except Exception as e:
            print(f"fail {ticker}_{kind}: {e}")
            continue
        with open(f"data/{ticker}_{kind}.json", "w") as f:
            json.dump(data, f)
        print(f"saved {ticker}_{kind}")
        time.sleep(0.2)                    # SEC 요청 속도 제한 준수
