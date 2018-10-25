# Base class for the news tools
from abc import ABCMeta, abstractmethod
import json
import os


class BaseSpider(metaclass=ABCMeta):
    __site_id = 1
    __silent = False
    __categories = []

    def __init__(self, site_id, silent, categories):
        self.__site_id = site_id
        self.__silent = silent
        self.__categories = categories

    def _print_progress(self, page_count):
        if not self.__silent:
            print('\rScraped: ' + str(page_count) + ' page(s)', end='')

    def _save_to_db(self, title, description, link, content, doc_id, cat_id):
        # setup JSON object
        doc = {'title': title, 'description': description, 'content': content, 'link': link}

        # setup new file to write to, and do it
        rel_path = 'crawled/' + str(self.__site_id) + '/' + str(cat_id) + '/' + str(doc_id) + '.json'
        abs_file_path = os.path.join(os.pardir, rel_path)
        with open(abs_file_path, 'w') as f:
            json.dump(doc, f)

        # setup temp file (to be post-tagged)
        temp_folder = os.path.join(os.pardir, 'post_tag/temp/')
        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        # write the temp file to disk
        rel_path = temp_folder + str(self.__site_id) + '_' + str(cat_id) + '_' + str(doc_id)
        with open(rel_path, 'w') as f:
            f.write('')

    def _doc_exists(self, new_link, last_link_id, cat_id):
        # checks if a document already exists in our collection, by comparing its link with the link we found online
        if last_link_id > 1:
            rel_path = 'crawled/' + str(self.__site_id) + '/' + str(cat_id) + '/' + str(last_link_id - 1) + '.json'
            abs_file_path = os.path.join(os.pardir, rel_path)
            with open(abs_file_path) as data_file:

                j = json.load(data_file)
                if j['link'] == new_link:
                    return True
        return False

    def _user_selections_are_valid(self, selections):
        # user input check
        if type(selections) is not list:
            print('Input Error: A list of numbers should be provided')
            return False
        for i in range(0, len(selections)):
            sel = selections[i]
            if type(sel) is not int:
                print('Input Error: A list of numbers should be provided')
                return False

            if sel < 0 or sel >= len(self.__categories):
                print('Input Error: The numbers in the input should be in the range of the categories: [0,' + str(
                    len(self.__categories) - 1) + ']')
                return False
        return True

    @staticmethod
    def _remove_duplicates(selections):
        ret = []
        for i in selections:
            if i not in ret:
                ret.append(i)
        return ret

    def _find_last_file_num_in_cat(self, cat):
        # find latest file number in category folder, so that we do not override older texts
        folder = os.path.join(os.pardir, 'crawled/' + str(self.__site_id) + '/' + str(cat))
        if not os.path.exists(folder):
            os.makedirs(folder)

        i = 1
        abs_file_path = folder + "/" + str(i) + ".json"

        while os.path.exists(abs_file_path):
            i += 1
            abs_file_path = folder + "/" + str(i) + ".json"
        return i

    # To be implemented by children
    @abstractmethod
    def _scrape_sublinks(self, pages, next_id):
        pass

    @abstractmethod
    def scrape_all(self):
        pass

    @abstractmethod
    def scrape_selected(self, selections):
        pass
