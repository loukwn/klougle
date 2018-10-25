import json
import os
from math import log

import nltk
from nltk.stem.wordnet import WordNetLemmatizer
import string


class PageIndexer:
    _temp_path = 'post_tag/temp'
    _vectorized_path = 'post_tag/vectorized'
    _master_path = 'post_tag/vectorized/master.json'
    _inv_idx_path = '../inv_index/inv_index.json'

    def __init__(self, clear_master=False):

        tagged_folder = os.path.join(os.pardir, self._vectorized_path)
        temp_folder = os.path.join(os.pardir, self._temp_path)

        if not os.path.exists(tagged_folder):
            os.makedirs(tagged_folder)
            self._init_master_file()

        if not os.path.exists(temp_folder):
            os.makedirs(temp_folder)

        if clear_master:
            self._init_master_file()

    def _init_master_file(self):
        full_path = os.path.join(os.pardir, self._master_path)
        with open(os.path.abspath(full_path), 'w') as f:
            f.write('{}')

    def _load_master_file(self):
        full_path = os.path.join(os.pardir, self._master_path)
        with open(full_path) as f:
            return json.load(f)

    def _save_master_file(self, dic):
        full_path = os.path.join(os.pardir, self._master_path)
        with open(full_path, 'w') as f:
            return json.dump(dic, f)

    @staticmethod
    def _get_text_from_original(filename):
        # we translate the file_id of the document, to find its original location on the disk and get its content
        temp = filename.split('_')
        partial_path = 'crawled/' + temp[0] + '/' + temp[1] + '/' + temp[2] + '.json'
        full_path = os.path.join(os.pardir, partial_path)
        with open(full_path) as f:
            j = json.load(f)
            return " ".join("".join([" " if ch in string.punctuation else ch for ch in j['content']]).split())

    @staticmethod
    def _remove_closed_class_categories(tagged):
        ret = []
        ban_list = ['CD', 'CC', 'DT', 'EX', 'IN', 'LS', 'MD', 'PDT', 'POS', 'PRP', 'PRP$', 'RP', 'TO', 'UH', 'WDT',
                    'WP', 'WP$', 'WRB']
        for term in tagged:
            if term[1] not in ban_list:
                ret.append(term)
        return ret

    @staticmethod
    def _add_content_to_master(J, content, filename):
        # we save all the terms of the content to the master file
        # the master file will contain for every term the docs that contain it and their frequency in them
        for term in content:
            if term[0] not in J:
                J[term[0]] = [{'id': filename, 'total': 1}]
            else:
                found = False
                for i in J[term[0]]:
                    if filename == i['id']:
                        i['total'] = i['total'] + 1
                        found = True
                        break

                if not found:
                    J[term[0]].append({'id': filename, 'total': 1})
        return J

    def _save_inv_index_file(self, J):
        full_path = os.path.join(os.pardir, self._inv_idx_path)
        with open(full_path, 'w') as f:
            return json.dump(J, f)

    @staticmethod
    def _update_index(J, N):
        # we use the master file to compute the final inverted index
        for key in J:
            total = len(J[key])
            for i in range(0, total):
                J[key][i]['w'] = J[key][i]['total'] * log(N / total)
                J[key][i].pop('total', None)
        return J

    def start(self):
        # we search the temporary folder for files to index
        abs_file_path = os.path.join(os.pardir, self._temp_path)
        untagged = [f for f in os.listdir(abs_file_path)]

        to_be_tagged = len(untagged)

        # if none are found we finish
        if to_be_tagged == 0:
            print('Nothing new to be tagged.')
            return

        # else we load the master file (explained in the report)
        wordnet_lemmatizer = WordNetLemmatizer()
        J = self._load_master_file()
        count = 0
        # and for every file
        for file in untagged:
            s = str(count)

            # we process it (tokenize, lemmatize, tag, remove closed class terms) and we add it to master
            content = self._get_text_from_original(file).strip()
            content_tokenized = [wordnet_lemmatizer.lemmatize(w.lower()) for w in nltk.tokenize.word_tokenize(content)]
            content_pos_tagged = nltk.pos_tag(content_tokenized)
            content_pos_tagged_no_closed = self._remove_closed_class_categories(content_pos_tagged)
            J = self._add_content_to_master(J, content_pos_tagged_no_closed, file)

            # we delete the temp file
            os.remove(abs_file_path + '/' + file)
            print('\r[' + s + '/' + str(to_be_tagged) + '] Tagged and added to index file: ' + file, end='')
            count += 1

        print('\r[' + str(to_be_tagged) + '/' + str(to_be_tagged) + '] All tagged and indexed! ')

        # finally we update the contents of the inverted index, using the contents of the master file
        print('Updating index.. ', end='')
        self._save_master_file(J)
        J = self._update_index(J, to_be_tagged)
        self._save_inv_index_file(J)
        print('OK')
