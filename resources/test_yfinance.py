import yfinance as yf


def get_company_profile(ticker):
    company = yf.Ticker(ticker)
    info = company.info

    # 주소 정보 합치기
    address_parts = []
    if info.get('address1'):
        address_parts.append(info.get('address1'))
    if info.get('address2'):
        address_parts.append(info.get('address2'))
    if info.get('city'):
        address_parts.append(info.get('city'))
    if info.get('state'):
        address_parts.append(info.get('state'))
    if info.get('zip'):
        address_parts.append(info.get('zip'))
    if info.get('country'):
        address_parts.append(info.get('country'))

    phone = info.get('phone', '')
    if phone:
        phone = phone.replace(' ', '-')

    # Industry와 Sector 정보 합치기
    industry_sector = f"{info.get('industry', 'N/A')} / {info.get('sector', 'N/A')}"

    # CEO 정보 가져오기 (첫 번째 사람의 이름만)
    ceo = info.get('companyOfficers', [{}])[0].get('name', 'N/A')

    return {
        'Industry Sector': industry_sector,
        'Address': ', '.join(filter(None, address_parts)),
        'Phone': phone,
        'CEO': ceo
    }


company_profile = get_company_profile("AAPL")
print(company_profile)
