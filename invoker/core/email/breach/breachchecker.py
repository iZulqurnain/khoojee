from requests import session
from bs4 import BeautifulSoup


# @TODO: Add breach search https://breachchecker.com/dashboard
class BreachChecker:
    __EMAIL__ = None

    def __init__(self, email):
        self.__EMAIL__ = email

    def check(self):
        pass
