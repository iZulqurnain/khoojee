from bs4 import BeautifulSoup
from requests import Session


class BuildWith:
    __DOMAIN__ = None

    def __init__(self, domain):
        self.__DOMAIN__ = domain

    @staticmethod
    def __technology_profile__(content):
        result = []
        soup = BeautifulSoup(content, 'html.parser')
        form = soup.find("div", {"class": "col-md-8 pr-1 pl-4"})
        headers = form.find_all("h2")
        for header in headers:
            img = header.find("img")
            result.append(
                {
                    "technology_name": header.text,
                    "technology_icon": img["data-src"]
                }
            )
        return result

    def check(self):
        information = {}
        session = Session()
        session.get("https://www.builtwith.com")
        re = session.get("https://builtwith.com/ebryx.com")
        information["technology"] = self.__technology_profile__(re.content)

        print(information)


obj = BuildWith("")
obj.check()
