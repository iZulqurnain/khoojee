import requests
import base64

sample_string = "master-ab@msn.com"
sample_string_bytes = sample_string.encode("ascii")

base64_bytes = base64.b64encode(sample_string_bytes)
base64_string = base64_bytes.decode("ascii")
print(base64_string)
header = {
    "authority": "www.lifelock.com",
    # "sec-ch-ua" : ""Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"",
    "dnt": "1",
    'Accept-Language': 'en-US,en;q=0.8',

    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "accept": "*/*",
    "csrf-token": "undefined",
    "x-requested-with": "XMLHttpRequest",
    "origin": "https://www.lifelock.com",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.lifelock.com/breach-detection/",
    "accept-language": "en-US,en;q=0.9",

}
payload = {
    "email": base64_string,
    "language": "en",
    "country": "us",
}
session = requests.Session()
session.get("https://www.lifelock.com/")
r = session.post(
    url="https://www.lifelock.com/bin/norton/lifelock/detectbreach"
    , json=payload, headers=header
)
print(r.content)
