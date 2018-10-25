# BBC Spider from its RSS using BeautifulSoup4

import requests
from bs4 import BeautifulSoup
from .basespider import BaseSpider

categories = ['http://feeds.bbci.co.uk/sport/rss.xml', 'http://feeds.bbci.co.uk/news/business/rss.xml',
              'http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml',
              'http://feeds.bbci.co.uk/news/technology/rss.xml',
              'http://feeds.bbci.co.uk/news/science_and_environment/rss.xml']


class BBCSpider(BaseSpider):
    __threshold = 30

    def __init__(self, silent=False, threshold=30):
        BaseSpider.__init__(self, 3, silent, categories)
        self.__threshold = threshold

    def _scrape_sublinks(self, pages, next_id):
        scraped = 0
        curr_cat = pages[0][3]
        sub_count = next_id - 1

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
            parent = doc.find('div', {'class': 'story-body'})
            if not parent:
                continue
            possibleNewParent = parent.find('div', {'class': 'story-body__inner'})
            if possibleNewParent:
                parent = possibleNewParent
            if parent:
                for p in parent.findAll('p'):
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
