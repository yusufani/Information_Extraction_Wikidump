import argparse
import pandas as pd
import time
import tqdm
import os
import requests

os.makedirs("Logs", exist_ok=True)

# %%
parser = argparse.ArgumentParser()
parser.add_argument('--yago',
                    default="datas/yago-wd-sameAs.nt",
                    help='Path of wikidata')
parser.add_argument('--kbpedia',
                    default="datas/wikidata.csv",
                    help='Name of output txt file')

parser.add_argument('--enwikidata',
                    default='datas/enwiki-20200901-pages-articles_wikidata_labeled.tsv',
                    help='Path of enwiki output tsv data')

parser.add_argument('--output_file',
                    default="datas/enwiki-20200901-pages-articles_out.tsv",
                    help='Name of output txt file')

args = parser.parse_args()
start = time.time()

YAGO = args.yago
OUTPUT_FILE = args.output_file
ENWIKIDATA = args.enwikidata
KBPEDIA = args.kbpedia

df_kpbedia = pd.read_csv(KBPEDIA)
kbpedia = {}

for idx,val in df_kpbedia.iterrows():
    label = val.values[0].split('/')[-1]
    kp = val.values[2].split('/')[-1]
    kbpedia[label] =kp
    #x = requests.get(val.values[2])

yago = {}
with open(YAGO,'r',encoding='utf-8') as fp:
    for i in fp.readlines():
        fields = i.replace('<','>').replace('>','').split('\t')
        label = fields[2].split('/')[-1]
        yg = fields[0]
        yago[label] = yg

df_main = pd.read_csv(ENWIKIDATA, delimiter='\t')
df_main['yago'] = 'None'
df_main['kbpedia'] = 'None'
for idx,val in df_main.iterrows():
    label = val.wikidata_label
    df_main.loc[idx, 'yago'] = yago.get(label,'None')
    df_main.loc[idx, 'kbpedia'] = kbpedia.get(label, 'None')

df_main = pd.read_csv(OUTPUT_FILE, delimiter='\t')


