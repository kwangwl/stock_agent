import requests
import time
import re


# config
MAX_PAGE = 2
REMOVE_COIN = ["리스크", "risk"]


def get_all_coins(locale):
    all_coins = []
    page = 1

    while True:
        print(page)
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": "krw",
            "order": "market_cap_desc",
            "per_page": 250,
            "page": page,
            "locale": locale
        }

        response = requests.get(url, params=params)
        coins = response.json()

        if page > MAX_PAGE:
            break

        all_coins.extend(coins)
        page += 1
        time.sleep(3)

    return all_coins


def clean_coin_name(name):
    # 소문자로 변환
    name = name.lower()

    # 코인으로 시작하거나 끝나는 경우 처리
    if re.match('^코인.*', name) or re.match('.*코인$', name):
        name = name.replace('코인', '')

    # coin으로 시작하거나 끝나는 경우 처리 (대소문자 구분 없이)
    if re.match('(?i)^coin.*', name) or re.match('(?i).*coin$', name):
        name = re.sub('(?i)coin', '', name)

    # 앞뒤 공백 제거
    name = name.strip()

    # 띄어쓰기 기준으로 3단어까지만 유지
    words = name.split()
    if len(words) > 3:
        name = ' '.join(words[:3])

    return name


# 실행
ko_coins = get_all_coins("ko")
en_coins = get_all_coins("en")
unique_names = set()  # 중복 제거를 위한 set

# 중복 제거하면서 이름 정제
for ko_coin, en_coin in zip(ko_coins, en_coins):
    ko_name = clean_coin_name(ko_coin['name'])
    en_name = clean_coin_name(en_coin['name'])

    if ko_name and ko_name not in REMOVE_COIN:  # 한글 이름 추가
        unique_names.add(ko_name)
    if en_name and en_name not in REMOVE_COIN:  # 영어 이름 추가
        unique_names.add(en_name)

# 정렬된 상태로 파일에 저장
with open('./cryptocurrency_names.txt', 'w', encoding='utf-8') as f:
    for name in sorted(unique_names):
        if name not in REMOVE_COIN:
            f.write(name + '\n')

print(f"총 {len(unique_names)}개의 고유한 코인 이름이 cryptocurrency_names.txt 파일에 저장되었습니다.")
