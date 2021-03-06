import requests
from bs4 import BeautifulSoup

from khoojee.settings import CELL_SAA


class SimLocation:
    __MOBILE_NUMBER__ = None

    def __init__(self, mobile_number):
        self.__MOBILE_NUMBER__ = mobile_number

    def __request__(self):
        information = {
            'network': None,
            'city': None,
            'status': None,
        }
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            payload = {'mobilenumber': self.__MOBILE_NUMBER__, 'submit': 'Search', 'submitse': 'Trace'}
            response = requests.post(url=CELL_SAA, headers=headers, data=payload)
            soup = BeautifulSoup(response.content, 'html.parser')
            data = soup.find("div", {"class": "art-content"})
            rows = data.findAll("div", {"class": "Cell"})

            i = 0
            for row in rows:

                content_element = row.find_all('b')
                for key_element in content_element:
                    if i == 1:
                        information['network'] = key_element.text
                    elif i == 2:
                        information['city'] = key_element.text
                    elif i == 3:
                        information['status'] = key_element.text
                    i = i + 1

        except Exception as e:
            print(e)

        if not information['network']:
            code = self.__MOBILE_NUMBER__[:4]
            num = self.__MOBILE_NUMBER__[4:]
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                payload = {'code': code, 'num': num, 'n': 'PKtech', 'send.x': '131', 'send.y': '31'}
                response = requests.post(url="http://charagh.com/mobile-directory/index.php", headers=headers,
                                         data=payload)
                soup = BeautifulSoup(response.content, 'html.parser')
                print(soup)
                data = soup.findAll("center")[0]
                content = str(data.get_text()).split('is ')[1]
                city, network = content.split(' Network :')
                information['city'] = city
                information['network'] = network
            except Exception as e:
                print(e)
        return information

    def get_report(self):
        return self.__request__()
