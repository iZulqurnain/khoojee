import hashlib
import requests
from bs4 import BeautifulSoup
import json

from khoojee.settings import DOMAIN_BIG_DATA


class DomainBigData:
    __DOMAIN__ = None

    __DOMAIN_BIG_DATA__ = DOMAIN_BIG_DATA

    def __init__(self, domain=None):
        if domain:
            self.__DOMAIN__ = domain

    @staticmethod
    def __extract_table_data__(soup):
        information = {}
        try:
            table = soup.find("table", {"class": "websiteglobalstats"})
            rows = table.findAll('tr')
            for row in rows[1:]:
                columns = row.findAll('td')
                if len(columns) >= 2 and columns[0].text != "":
                    information[columns[0].text] = columns[1].text
        except AttributeError:
            pass
        return information

    def __extract_domain_information__(self, soup):
        soup = soup.find("div", {"id": "idCardWebsite"})
        return self.__extract_table_data__(soup)

    def __extract_registrant_information__(self, soup):
        soup = soup.find("div", {"id": "idCardRegistrant"})
        return self.__extract_table_data__(soup)

    @staticmethod
    def __whois_table_data__(soup):
        whois = soup.find("div", {"class": "col-md-12 pd5 mt10"})
        whois_record = {}
        for record in str(whois).split('<br/>'):
            if len(record.split(": ")) == 2:
                key, value = record.split(": ")
                if 'Domain Name' in key:
                    key = "Domain Name"
                if "\r\n" in value:
                    value = value.split('\r')[0]
                whois_record[key] = value
        return whois_record

    def __parse_whois_information__(self, soup):
        information = {}
        try:
            soup = soup.find("div", {"id": "whois"})
            last_update = soup.find("small", {"class": "fright light"}).text.split(":")
            if self.__whois_table_data__(soup):
                information["last update"] = last_update[1]
                information["whois_details"] = self.__whois_table_data__(soup)
        except AttributeError:
            pass
        return information

    def __extract_historic_registrant__(self, soup):
        soup = soup.find_all("div", {"id": "divRptHistoryMain"})
        information = []
        for record in soup:
            if self.__whois_table_data__(record):
                record_data = record.find("h2", {"class": "h2InRpt"})
                information.append(
                    {
                        'record_date': record_data.text.split(":")[1],
                        'whois_info': self.__whois_table_data__(record)
                    }
                )
        return information

    @staticmethod
    def __similar_domain__(soup):
        same_domain_list = []
        try:
            soup = soup.find("div", {"id": "divListOtherTLD"})
            for url in soup.find_all('a'):
                if url.text not in same_domain_list:
                    same_domain_list.append(url.text)
        except AttributeError:
            pass
        return same_domain_list

    @staticmethod
    def __extract_name_servers__(soup):
        name_server = {}
        title = ""
        try:
            soup = soup.find("div", {"id": "divDNSRecords"})
            for record in str(soup).split("<h3>"):
                try:
                    soup = BeautifulSoup("<h3>" + record, 'html.parser')
                    title = soup.find("h3").text
                    if "A Records" == title:
                        name_server[title] = []
                        table = soup.find("table")
                        for row in table.findAll('tr'):
                            value = row.findAll('td')
                            record = {
                                "Type": value[0].string,
                                "Hostname": value[1].string,
                                "Address": value[2].string,
                                "TTL": value[3].string,
                                "Class": value[4].string,

                            }
                            if record not in name_server[title]:
                                name_server[title].append(record)

                    elif "AAAA Records" in title:
                        name_server[title] = []
                        table = soup.find("table")
                        for row in table.findAll('tr'):
                            value = row.findAll('td')
                            record = {
                                "Type": value[0].string,
                                "Hostname": value[1].string,
                                "Address": value[2].string,
                                "Class": value[3].string,

                            }
                            if record not in name_server[title]:
                                name_server[title].append(record)

                    elif "MX Records" in title:
                        name_server[title] = []
                        table = soup.find("table")
                        for row in table.findAll('tr'):
                            value = row.findAll('td')
                            record = {
                                "Type": value[0].string,
                                "Hostname": value[1].string,
                                "Address": value[2].string,
                                "Preference": value[3].string,
                                "Class": value[4].string,

                            }
                            if record not in name_server[title]:
                                name_server[title].append(record)
                    elif "CNAME Records" in title:
                        name_server[title] = []
                        table = soup.find("table")

                except AttributeError:
                    pass
        except AttributeError:
            pass
        return name_server

    @staticmethod
    def __name_server_history__(soup):
        results = []

        try:
            soup = soup.find("div", {"id": "MainMaster_divNSHistory"})
            table = soup.find("table")
            for row in table.findAll('tr')[1:]:
                value = row.findAll('td')
                record = {
                    "date": value[0].string,
                    "status": value[1].string,
                    "name server": value[2].string
                }
                results.append(record)
        except AttributeError:
            pass
        return results

    def __parse_response__(self, html_content):
        results = {}
        soup = BeautifulSoup(html_content, 'html.parser')
        domain_info = self.__extract_domain_information__(soup)
        results["basic_domain_info"] = domain_info

        registrant_info = self.__extract_registrant_information__(soup)
        results["registrant_info"] = registrant_info

        whois_info = self.__parse_whois_information__(soup)
        results["whois_info"] = whois_info

        history_info = self.__extract_historic_registrant__(soup)
        results["domain_registrant_history_info"] = history_info

        same_domain = self.__similar_domain__(soup)
        results["other_TLDs"] = same_domain

        name_servers = self.__extract_name_servers__(soup)
        results["name_server"] = name_servers

        name_servers_history = self.__name_server_history__(soup)
        results["name_server_history"] = name_servers_history

        return results

    def __download_report__(self):
        if self.__DOMAIN__:
            url = self.__DOMAIN_BIG_DATA__ + self.__DOMAIN__
            response = requests.get(url=url)
            result = self.__parse_response__(response.content)
            return json.dumps(result, indent=2)

    @staticmethod
    def __write_json__(file_name, content):

        with open(str(file_name) + ".json", "w") as outfile:
            outfile.write(content)

    def get_report(self, domain=None):
        if domain:
            self.__DOMAIN__ = domain
        report = self.__download_report__()
        file_name = abs(hash(self.__DOMAIN__)) % (10 ** 8)
        self.__write_json__(file_name, content=report)
        return file_name


obj = DomainBigData("thepkmkb.com")
print(obj.get_report())
