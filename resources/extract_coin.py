import requests
import time


def get_all_coins():
    all_coins = []
    page = 1

    while True:
        print(page)
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "krw",
            "order": "market_cap_desc",
            "per_page": 250,  # 한 페이지당 최대 개수
            "page": page,
            "locale": "ko"
        }

        response = requests.get(url, params=params)
        coins = response.json()

        # 더 이상 가져올 코인이 없으면 종료
        if page > 4:
            break

        all_coins.extend(coins)
        page += 1

        # API 호출 제한을 고려한 딜레이
        time.sleep(5)

    return all_coins


# 실행
coins = get_all_coins()
with open('../cryptocurrency_names.txt', 'w', encoding='utf-8') as f:
    for coin in coins:
        f.write(coin['name'] + '\n')

print(f"총 {len(coins)}개의 코인 이름이 cryptocurrency_names.txt 파일에 저장되었습니다.")
