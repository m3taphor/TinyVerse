import re

headers = {
    "Host": "api.tonverse.app",
    "Connection": "keep-alive",
    "sec-ch-ua-platform": "Windows",
    "sec-ch-ua": '"Chromium";v="132", "Microsoft Edge";v="132", "Not A(Brand";v="8", "Microsoft Edge WebView2";v="132"',
    "sec-ch-ua-mobile": "?0",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "*/*",
    "Origin": "https://app.tonverse.app",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://app.tonverse.app/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate"
}

def get_sec_ch_ua(user_agent):
    pattern = r'(Chrome|Chromium)\/(\d+)\.(\d+)\.(\d+)\.(\d+)'

    match = re.search(pattern, user_agent)

    if match:
        browser = match.group(1)
        version = match.group(2)

        if browser == 'Chrome':
            sec_ch_ua = f'"Chromium";v="{version}", "Not;A=Brand";v="24", "Google Chrome";v="{version}"'
        else:
            sec_ch_ua = f'"Chromium";v="{version}", "Not;A=Brand";v="24"'

        return {'Sec-Ch-Ua': sec_ch_ua}
    else:
        return {}
