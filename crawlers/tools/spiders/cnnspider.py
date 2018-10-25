# CNN Spider from its RSS using BeautifulSoup4

import requests
from bs4 import BeautifulSoup
from .basespider import BaseSpider

categories = ['http://rss.cnn.com/rss/edition_sport.rss', 'http://rss.cnn.com/rss/money_news_international.rss',
              'http://rss.cnn.com/rss/edition_entertainment.rss', 'http://rss.cnn.com/rss/edition_technology.rss',
              'http://rss.cnn.com/rss/edition_space.rss']


class CNNSpider(BaseSpider):

    __threshold = 30

    def __init__(self, silent=False, threshold=30):
        BaseSpider.__init__(self, 1, silent, categories)
        self.__threshold = threshold

    @staticmethod
    def __is_valid_line(line):
        ban_list = ['READ: ', 'WATCH: ', 'Go to CNN.com/']  # Learn more, --
        for ban_word in ban_list:
            if line.startswith(ban_word):
                return False
        return True

    def _scrape_sublinks(self, pages, base_id):
        scraped = 0
        curr_cat = pages[0][3]
        sub_count = base_id-1

        for page in reversed(pages):
            if self.__threshold != -1 and scraped == self.__threshold:
                break
            if curr_cat != page[3]:
                curr_cat = page[3]
                sub_count = 0
            r = requests.get(page[2])
            doc = BeautifulSoup(r.text, 'lxml')
            content = ""
            if page[0] == '':
                page[0] = doc.title.string

            # the known way
            if doc.find('div', {'class': 'zn-body__paragraph'}):
                for p in doc.findAll('div', {'class': 'zn-body__paragraph'}):
                    if self.__is_valid_line(p.text):
                        content += ' ' + p.text

                scraped += 1
                sub_count += 1
                self._save_to_db(page[0], page[1], page[2], content, sub_count, page[3])
                if scraped <= len(pages):
                    self._print_progress(scraped)
                continue

            # the other way
            parent = doc.find('div', {'id': 'storytext'})
            if parent:
                for p in parent.findAll('p'):
                    if self.__is_valid_line(p.text):
                        content += ' ' + p.text

                scraped += 1
                sub_count += 1
                self._save_to_db(page[0], page[1], page[2], content, sub_count, page[3])
                if scraped <= len(pages):
                    self._print_progress(scraped)
                continue

            # the rare way
            parent = doc.find('div', {'class': 'Article__body'})
            if parent:
                for p in parent.findAll('p', {'class': 'Paragraph__component'}):
                    if self.__is_valid_line(p.text):
                        content += ' ' + p.text

                scraped += 1
                sub_count += 1
                self._save_to_db(page[0], page[1], page[2], content, sub_count, page[3])
                if scraped <= len(pages):
                    self._print_progress(scraped)

            # the science
            parent = doc.find('div', {'id': 'cnnTxtCmpnt'})
            if parent:
                for p in parent.findAll('p'):
                    if self.__is_valid_line(p.text):
                        content += ' ' + p.text

                scraped += 1
                sub_count += 1
                self._save_to_db(page[0], page[1], page[2], content, sub_count, page[3])
                if scraped <= len(pages):
                    self._print_progress(scraped)
        print('\n')

    def scrape_all(self):
        count = 0
        for cat in categories:
            pages = []
            next_id = self._find_last_file_num_in_cat(count)
            r = requests.get(cat)

            doc = BeautifulSoup(r.text, 'lxml')
            for item in doc.findAll('item'):
                title = item.find('title').text
                desc = item.find('description').text
                link = item.find('link').text
                if link == '':
                    link = item.link.next_sibling.strip()
                if desc.startswith('<img'):
                    desc = ''
                if self._doc_exists(link, next_id, count):
                    break
                pages.append([title, desc, link, count])

            if len(pages) > 0:
                print('Scraping from: ' + categories[count])
                self._scrape_sublinks(pages, next_id)
            count += 1

    def scrape_selected(self, selections):
        if self._user_selections_are_valid(selections):
            selections = self._remove_duplicates(selections)
            for i in selections:
                pages = []
                next_id = self._find_last_file_num_in_cat(i)
                r = requests.get(categories[i])

                doc = BeautifulSoup(r.text, 'lxml')
                for item in doc.findAll('item'):
                    title = item.find('title').text
                    desc = item.find('description').text
                    link = item.find('link').text
                    if link == '':
                        link = item.link.next_sibling.strip()
                    if desc.startswith('<img'):
                        desc = ''
                    if self._doc_exists(link, next_id, i):
                        break
                    pages.append([title, desc, link, i])

                if len(pages) > 0:
                    print('Scraping from: ' + categories[i])
                    self._scrape_sublinks(pages, next_id)
