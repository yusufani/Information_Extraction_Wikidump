import os
from Enwikiparser import *
from data_reader import *

import time
import argparse
os.makedirs("Logs",exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('--input',
                    default="/mnt/minerva1/nlp/corpora_datasets/monolingual/english/wikipedia/text_extracted_by_wikiextractor_from_enwiki-20210101-pages-articles.txt",
                    help='You can give text folder or single file')
parser.add_argument('--output',
                    default="datas/enwiki-20200901-pages-articles_title_first_phrases_words.tsv",
                    help='Name of output tsv file')
args = parser.parse_args()

WIKIDATA_DICT = args.input
OUTPUT_PATH = args.output
p = Parser()

KEYS = ["title", "alternative_names", "first_sentence", "defining_pharases", "defining_words", 'nationality']

start = time.time()

result = []


def input_iterator(WIKIDATA_DICT):
    if os.path.isfile(WIKIDATA_DICT):
        f = open(WIKIDATA_DICT, encoding='utf-8')
        batch_size = 10_000
        return read_from_single_file(f, batch_size)
    else:
        all_datas = read_all_files(WIKIDATA_DICT, [])
        return read_from_multiple_files(all_datas)


for idx, data in enumerate(input_iterator(WIKIDATA_DICT)):
    if idx % 10 == 0:
        if idx == 0:
            p.save_results(OUTPUT_PATH, KEYS, result, first=True)
        else:
            print("Saving results...")
            p.save_results(OUTPUT_PATH, KEYS, result)
        result = []
    pages = p.split_pages(data)
    for page in pages[:-1]:
        title, alternative_names, first_sentence, def_pharases, def_words, nationality = p.get_informations(page)
        if title != False:
            print("Title: " + title)
            result.append({"title": title, "alternative_names": alternative_names, "first_sentence": first_sentence,
                           "defining_pharases": def_pharases, "defining_words": def_words,
                           'nationality': nationality})

end = time.time()
with open("Time.txt", "w") as fp:
    fp.write("Time:" + str(end - start))

print("Process finished. Total time :", end - start, " seconds")
