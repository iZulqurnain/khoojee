# @TODO: https://spyse.com/target/domain/codebryx.com <== work on it
import requests
from bs4 import BeautifulSoup as bs
# https://stackoverflow.com/questions/53032456/login-with-python-requests-and-csrf-token
session = requests.Session()
r = session.get("https://dnsdumpster.com/")
print(session.cookies.get_dict())

payload = {
    "targetip":"www.ebryx.com",
    "csrfmiddlewaretoken": session.cookies.get_dict()["csrftoken"],
}

print(session.post(url="https://dnsdumpster.com/", json=payload))