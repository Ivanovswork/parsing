from bs4 import BeautifulSoup
import requests
from fake_headers import Headers
import json



headers = Headers(os="win", browser="chrome")


def get_page(url):
    return requests.get(url, headers=headers.generate())


def get_vacancys(num_page):
    vac = []
    for i in range(0, num_page):
        url = f"https://kaluga.hh.ru/search/vacancy?no_magic=true&L_save_area=true&text=python&excluded_text=&area=1&area=2&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=50&page={i}&hhtmFrom=vacancy_search_list"
        ret = get_page(url).text
        soup = BeautifulSoup(ret, features='html5lib')
        vacancys = soup.find_all(class_="serp-item")
        vac.extend(vacancys)
    return vac


def get_links(num_page):
    links = []
    for elem in get_vacancys(num_page):
        t = " "
        if elem.find(class_="g-user-content"):
            t = elem.find(class_="g-user-content").text
        if "Django" in t or "Flask" in t:
            link = elem.find("a")["href"]
            links.append(link)
    return links


def parse(links):
    data = {}
    for link in links:

        vac = get_page(link)
        soup = BeautifulSoup(vac.text, features='html5lib')
        title = soup.find("h1", {"data-qa": "vacancy-title"}).text
        salary = soup.find("div", {"data-qa": "vacancy-salary"}).text
        try:
            city = soup.find("p", {"data-qa": "vacancy-view-location"}).text
        except BaseException:
            city = list(soup.find("span", {"data-qa": "vacancy-view-raw-address"}).text.split())[0][:-1]
        company = soup.find("a", {'data-qa': 'vacancy-company-name'}).text
        data[title] = {
            "link": link,
            "salary": salary,
            "city": city,
            "company": company
        }
    return data


if __name__ == '__main__':
    num_page = 5
    with open("data_file.json", "w", encoding="utf-8") as write_file:
        json.dump(parse(get_links(num_page)), write_file, ensure_ascii=False, indent=2)