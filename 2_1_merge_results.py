#%%
import os
import pandas as pd
import time
from tqdm import tqdm
import argparse

os.makedirs("Logs",exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('--alternative_names',
                    default="datas/enwiki-20200901-pages-articles_alternative_names.csv",
                    help='Path of alternative_names csv')
parser.add_argument('--main_tsv',
                    default="datas/enwiki-20200901-pages-articles_title_first_phrases_words.tsv",
                    help='Path of main csv file ')
parser.add_argument('--output',
                    default="datas/enwiki-20200901-pages-articles_merged.tsv",
                    help='Name of output final tsv file')
args = parser.parse_args()


ALTERNATIVE_NAMES = args.alternative_names
TITLE_FIRST_PHRASES_WORDS = args.main_tsv

OUTPUT_NAME = args.output
#%%
start = time.time()
df_main = pd.read_csv(TITLE_FIRST_PHRASES_WORDS,delimiter='\t')
print(TITLE_FIRST_PHRASES_WORDS, ' is read')
#%%

df_alternative = pd.read_csv(ALTERNATIVE_NAMES,delimiter='###').to_dict()
print(ALTERNATIVE_NAMES, ' is read')
#%%
print('Process starting ... ')
for idx,row in tqdm(df_main.iterrows()):
    tmp = '' if str(row['alternative_names']) == 'None' else row['alternative_names']
    df_main.at[0,'alternative_names'] = str(df_alternative[row['title']]) if df_alternative.get(row['title'],False) else 'None'
end = time.time()
#%%
df_main.to_csv(OUTPUT_NAME,sep='\t')
print('Data is ready ' + OUTPUT_NAME +' Taken time :' + str(end-start))

