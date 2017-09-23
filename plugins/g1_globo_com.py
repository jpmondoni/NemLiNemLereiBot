import datetime
import requests
import re
from bs4 import BeautifulSoup


class Plugin():

    def register_plugin(self, PluginManager):
        PluginManager.register_plugin(
            'g1_globo_com', r"^https?://g1.globo.com((?!/google/amp/))(.*)/noticia/(.*).ghtml$")

    def extract_metadata(self, url):
        self.url = url
        self.page_html = self.request_page()
        self.soup = self.get_soup()
        self.get_content()
        return {'subtitle': self.get_title(),
                'date_published': self.get_date(),
                'content': self.get_content()}

    def get_title(self):
        soup = self.soup
        subtitle = soup.select_one('.content-head__subtitle')
        return subtitle.get_text()

    def get_date(self):
        soup = self.soup
        date = soup.select_one('time[itemprop="datePublished"]').get_text()
        match_date = re.search(r'(\d{2})/(\d{2})/(\d{4})', date).group(0)
        date_published = datetime.datetime.strptime(match_date, "%d/%m/%Y").date()
        return date_published

    def get_content(self):
        soup = self.soup
        paragraphs_list = []
        paragraphs = soup.find_all(
            "p", re.compile(r"content-text__container(.*)"))
        for paragraph in paragraphs:
            if len(paragraph.text) > 20:
                paragraphs_list.append(paragraph.text.strip())
        return ' '.join(paragraphs_list)

    def request_page(self):
        r = requests.get(self.url)
        if r.status_code == 200:
            html_page = r.text
        return html_page

    def get_soup(self):
        soup = BeautifulSoup(self.page_html, 'html.parser')
        return soup