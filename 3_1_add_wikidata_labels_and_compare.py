import argparse
import pandas as pd
import time
import tqdm
import os
os.makedirs("Logs", exist_ok=True)

# %%
parser = argparse.ArgumentParser()
parser.add_argument('--wikidata',
                    default="datas/wikidata-20201214-all-BETA.nt.qldwaiso.in_en_wikipedia",
                    help='Path of wikidata')
parser.add_argument('--output_log',
                    default="datas/wikidata_comparision.txt",
                    help='Name of output txt file')
parser.add_argument('--output_file',
                    default="datas/enwiki-20200901-pages-articles_wikidata_labeled.tsv",
                    help='Name of output txt file')
parser.add_argument('--enwikidata',
                    default='datas/enwiki-20200901-pages-articles_merged.tsv',
                    help='Path of enwiki output tsv data')
args = parser.parse_args()
start = time.time()
OUTPUT_LOG = args.output_log
OUTPUT_FILE = args.output_file
ENWIKIDATA = args.enwikidata
WIKIDATA = args.wikidata

df_main = pd.read_csv(ENWIKIDATA, delimiter='\t')
df_main['wikidata_label'] = 'None'

print('Enwikidata is loaded')


def get_sentences_from_line(line):
    fields = line.split('P106=')[1].replace('\n', '').replace('|', '-').split('-')
    return [i.strip() for idx, i in enumerate(fields) if idx % 2 == 1]


EXACT_TRUE_WORDS = 0 # The case both of sentences are equal
EXACT_TRUE_PHRASES = 0
EXACT_TRUE_NATION = 0
EXACT_TRUE_ONE_OF = 0

PART_OF_TRUE_WORD= 0 # If 1 of word in sentence
PART_OF_PHRASES = 0
PART_OF_TRUE_NATION = 0
PART_OF_TRUE_ONE_OF = 0

FOUNDED_WORDS = 0
NUMBER_OF_TITLE = 0

ft = 0  # Found titles
nt = 0  # Not found titles
nl = 0  # Number of lines


def print_stats():
    if FOUNDED_WORDS > 0 :
        result = 'Number of title found : ' + str(NUMBER_OF_TITLE) + '\n'
        result += 'Number of extracted words from wikidata : ' + str(FOUNDED_WORDS) + '\n'
        result += 'EXACT True Words ' + str(EXACT_TRUE_WORDS) + ' Accuracy:' + str(EXACT_TRUE_WORDS / FOUNDED_WORDS) + '\n'
        result += 'EXACT True Phrases ' + str(EXACT_TRUE_PHRASES) + ' Accuracy:' + str(
            EXACT_TRUE_PHRASES / FOUNDED_WORDS) + '\n'
        result += 'EXACT True Nation ' + str(EXACT_TRUE_NATION) + ' Accuracy:' + str(
            EXACT_TRUE_NATION / FOUNDED_WORDS) + '\n'
        result += 'EXACT True Words or Phrases or nationality: ' + str(EXACT_TRUE_ONE_OF) + ' Accuracy:' + str(
            EXACT_TRUE_ONE_OF / FOUNDED_WORDS) + '\n'

        result += 'PART OF True Words ' + str(PART_OF_TRUE_WORD) + ' Accuracy:' + str(
            PART_OF_TRUE_WORD / FOUNDED_WORDS) + '\n'
        result += 'PART OF True Phrases ' + str(PART_OF_PHRASES) + ' Accuracy:' + str(
            PART_OF_PHRASES / FOUNDED_WORDS) + '\n'
        result += 'PART OF True Nation ' + str(PART_OF_TRUE_NATION) + ' Accuracy:' + str(
            PART_OF_TRUE_NATION / FOUNDED_WORDS) + '\n'
        result += 'PART OF True Words or Phrases or nationality: ' + str(PART_OF_TRUE_ONE_OF) + ' Accuracy:' + str(
            PART_OF_TRUE_ONE_OF / FOUNDED_WORDS) + '\n'
        print(result)
    else:
        result= 'Didnt find suitable match'
    return result

wiki_labels= {}
print('Processing Wikidata')
with open(WIKIDATA, 'r', encoding='utf8') as fp:
    for line in fp.readlines():
        if nl % 10_000 == 0 :
            print('Line number' , nl)
        nl += 1
        if 'P106=' in line:  # Words included
            title = line.split('\t')[1]
            wiki_labels[title]=[line.split('\t')[0],get_sentences_from_line(line)]
print('Wikidata Processed.Data merging and comparing')
for idx,val in df_main.iterrows():
    fields = wiki_labels.get(val.title,'not_found')
    if idx % 1000 == 1:
        print('Step {} / {} -> %{} '.format(idx,len(df_main),100*idx/len(df_main)) )
        print_stats()
    if fields != 'not_found':
        ft += 1
        NUMBER_OF_TITLE += 1
        df_main.loc[idx,'wikidata_label'] = fields[0]
        words = [i.strip() for i in val.defining_words.split('|')]
        phrases = [i.strip() for i in val.defining_pharases.split('|')]
        nationality = [i.strip() for i in val.nationality.split('|')]
        FOUNDED_WORDS += len(fields[1])

        #print('Title:', title)
        #print('Found words:', words)
        #print('Found Phrases:', phrases)
        #print('Found Nations',nationality)
        #print("WIKIDATA P106 = : ", wikidata_sentences)
        #print(50 * '*')

        for sentence in fields[1]:
            found = False
            if sentence in words:
                found = True
                EXACT_TRUE_WORDS += 1
                PART_OF_TRUE_WORD +=1
            if sentence in phrases:
                found = True
                EXACT_TRUE_PHRASES += 1
                PART_OF_PHRASES += 1
            if sentence in nationality:
                found = True
                EXACT_TRUE_NATION +=1
                PART_OF_TRUE_NATION +=1
            if found:
                EXACT_TRUE_ONE_OF += 1
                PART_OF_TRUE_ONE_OF+=1
            else:
                sentence = sentence.split()
                words_flat = []
                for i in words:
                    words_flat = [*words_flat, *(i.split()) ]
                phrases_flat = []
                for i in words:
                    phrases_flat= [*phrases_flat, *(i.split()) ]
                nationality_flat = []
                for i in words:
                    nationality_flat= [*nationality_flat, *(i.split()) ]

                for i in sentence:
                    found = False
                    if i in words_flat:
                        found = True
                        PART_OF_TRUE_WORD += 1
                    if i in phrases_flat:
                        found = True
                        PART_OF_PHRASES += 1
                    if i in nationality_flat:
                        found = True
                        PART_OF_TRUE_NATION += 1
                    if found:
                        PART_OF_TRUE_ONE_OF += 1
    else:
        nt += 1

df_main.to_csv(OUTPUT_FILE,sep='\t')
result = print_stats()
result += 'Passed Time in seconds: ' + str(time.time() - start) + '\n'
print('Found titles {} , Not found titles {} , Number of lines {}'.format(ft, nt, nl))

with open(OUTPUT_LOG, 'w') as fp:
    fp.write(result)

print(result)
