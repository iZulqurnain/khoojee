import random
import time
from bs4 import BeautifulSoup
import certifi
import ssl
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager


class SimData:
    __MOBILE_NUMBER__ = None
    __SERVER_ONE__ = "https://simdatabaseonline.com/tele/search-result.php"

    def __init__(self, mobile_number):
        self.__MOBILE_NUMBER__ = mobile_number

    def __session_request__(self):
        number_details = {
            'phone_number': None,
            'cnic': None,
            'date': None,
            'name': None,
            'address': None,
            'address1': None,
            'address2': None,
            'city': None,
            'other_phone': None,
            'first_name': None,
            'last_name': None,
        }
        s = requests.Session()
        s.trust_env = False
        s.verify = certifi.where()
        try:
            user_agent_list = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            ]
            user_agent = random.choice(user_agent_list)

            if not len(self.__MOBILE_NUMBER__) == 10:
                return False, None
            payload = {'cnnum': self.__MOBILE_NUMBER__}
            headers = {
                'authority': 'simdatabaseonline.com',
                'cache-control': 'max-age=0',
                'user-agent': user_agent,
                'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                'origin': 'https://simdatabaseonline.com',
                'upgrade-insecure-requests': '1',
                'dnt': '1',
                'content-type': 'application/x-www-form-urlencoded',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/'
                          'apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'referer': 'https://simdatabaseonline.com/tele/search.php?msg=Please%20Enter%20atleast%201%20'
                           'Mobile%20Number%20or%20CNIC',
                'accept-language': 'en-US,en;q=0.9',
            }
            s.headers = headers
            s.get(self.__SERVER_ONE__)

            response = s.post(self.__SERVER_ONE__,
                              data=payload)
            print(response.headers)

            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find(lambda tag: tag.name == 'table')
            rows = table.findAll(lambda tag: tag.name == 'tr')
            if rows:
                for row in rows:
                    content_element = row.find_all('td')
                    is_key = True
                    key_elem = None
                    for key_element in content_element:
                        if is_key:

                            key_elem = key_element.text
                            is_key = False
                        else:
                            if 'otherphone' in key_elem and len(key_element.text) > 3:
                                number_details['other_phone'] = key_element.text
                                # number_details['other_phone'] = ''
                            elif 'cnic' in key_elem and len(key_element.text) > 3:
                                number_details['cnic'] = key_element.text
                                # number_details['cnic'] = ''
                            elif 'date' in key_elem and len(key_element.text) > 3:
                                # number_details['date'] = ''
                                number_details['date'] = key_element.text
                            elif 'name' in key_elem and len(key_element.text) > 2:
                                number_details['name'] = str(key_element.text).title()
                            elif 'address' in key_elem and len(key_element.text) > 3:
                                number_details['address'] = key_element.text.title()
                                # number_details['address'] = ''
                            elif 'address1' in key_elem and len(key_element.text) > 3:
                                number_details['address1'] = key_element.text.title()
                            elif 'address2' in key_elem and len(key_element.text) > 3:
                                number_details['address2'] = key_element.text.title()
                                # number_details['address2'] = ''
                            elif 'city' in key_elem and len(key_element.text) > 3:
                                number_details['city'] = key_element.text.title()
                            elif 'lastname' in key_elem and len(key_element.text) > 2:
                                number_details['last_name'] = key_element.text.title()
                            elif 'firstname' in key_elem and len(key_element.text) > 2:
                                number_details['first_name'] = key_element.text.title()

                try:
                    del number_details['number']
                except:
                    pass
                number_details['phone_number'] = '0092' + self.__MOBILE_NUMBER__

            return True, number_details
        except Exception as e:
            # print(response.headers)
            print(s.headers)
            print(e)
            return False, str(e)

    def get_report(self):
        retry = True
        tries = 0
        while retry:
            print("Collecting sim data for " + str(self.__MOBILE_NUMBER__) + ", try number " + str(tries + 1))
            status_code, content = self.__session_request__()
            if status_code:
                return status_code, content
            if "'NoneType' object has no attribute" in content:
                return status_code, content
            tries = tries + 1
            time.sleep(tries)
