import json
import operator
import os
import webbrowser
from timeit import default_timer as timer

from kivy.app import App
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivy.uix.stacklayout import StackLayout
from nltk.stem.wordnet import WordNetLemmatizer

Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

INV_IDX_NAME = 'inv_index.json'
_wordnet_lemmatizer = WordNetLemmatizer()
_wordnet_lemmatizer.lemmatize('asd')


def get_data_from_json():
    # loads the inverted index in memory
    rel_path = "inv_index/" + INV_IDX_NAME
    abs_file_path = os.path.join(os.pardir, rel_path)
    with open(abs_file_path) as data_file:
        return json.load(data_file)


def get_doc_details(key):
    # uses the id of the document to find its location in disk and then returns its title and its link
    temp = key.split('_')
    partial_path = 'crawlers/crawled/' + temp[0] + '/' + temp[1] + '/' + temp[2] + '.json'
    abs_file_path = os.path.join(os.pardir, partial_path)
    with open(abs_file_path) as f:
        j = json.load(f)
        return [j['title'], j['link']]


def perform_query(query):
    # we process the query (split/lemmatize/turn to lowercase)
    terms = [_wordnet_lemmatizer.lemmatize(x.strip().lower()) for x in query.split()]
    data = get_data_from_json()

    # the dictionary that will hold the document results
    docs_returned = {}

    # we search for every term in the query the corresponing lemma in the inverted index
    for lemma in data:
        if lemma in terms:
            # if we find the the term in the inverted index
            for i in data[lemma]:
                # we add its weight to the docs_returned structure
                if i['id'] not in docs_returned:
                    docs_returned[i['id']] = i['w']
                else:
                    docs_returned[i['id']] += i['w']

    # we sort the docs based on their values (descending)
    sorted_x = sorted(docs_returned.items(), key=operator.itemgetter(1), reverse=True)
    to_return = []
    count = 1
    for key, value in sorted_x:
        # and for every doc we extract the title and link so that we can show them
        [title, link] = get_doc_details(key)
        title = str(count) + ') ' + title
        to_return.append([title, link, value])
        count += 1
    return to_return


# -------------------------- UI -------------------------- #
def open_url(text):
    # click an item to open the link to the browser
    webbrowser.open(text.split('\n')[0], new=2)


# top layout of UI
class SearchUI(StackLayout):
    statusLabel = ObjectProperty()
    resultList = ObjectProperty()
    searchInput = ObjectProperty()

    def add_result_to_list_view(self, title, link, weight):
        resized_link = link
        if len(resized_link) >= 102:
            resized_link = resized_link[0:102] + '...'

        content = link + '\n[size=16][b]' + title + '[/b][/size]\n-- [size=15][color=#757575][i]Weight: ' + str(
            weight) + '[/i][/color]\n[color=#3F51B5]' + resized_link + '[/size][/color]'
        self.resultList.adapter.data.extend([content])
        self.resultList._trigger_reset_populate()

    def go_pressed(self):
        query = self.searchInput.text.strip()
        if len(query) > 0:
            self.clear_list()
            self.statusLabel.text = "Searching.."
            start = timer()                    #
            results = perform_query(query)     # query to inverted index happens (and is timed) here
            end = timer()                      #
            if len(results) > 0:
                for doc in results:
                    self.add_result_to_list_view(doc[0], doc[1], doc[2])
                self.statusLabel.text = "Results: " + str(
                    len(self.resultList.adapter.data)) + "     (Time elapsed: " + "{:10.4f}s) ".format(end - start)
            else:
                self.statusLabel.text = "No results.."
        else:
            self.clear_list()
            self.statusLabel.text = 'Type some search terms and hit "Go"'

    def clear_list(self):
        del self.resultList.adapter.data[:]


# kivy app
class SearchApp(App):
    def build(self):
        return SearchUI()


# starting point
if __name__ == '__main__':
    SearchApp().run()
