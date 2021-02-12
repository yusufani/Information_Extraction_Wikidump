import xml.etree.ElementTree as etree
from tqdm import tqdm
import re
import time
import os
import argparse
os.makedirs("Logs",exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument('--wiki_dictionary',
                    default="/mnt/data/nlp/corpora_datasets/monolingual/english/wikipedia/split_enwiki-20191001-pages-articles",
                    help='Path of dump files dictionary')
parser.add_argument('--output',
                    default="datas/enwiki-20200901-pages-articles_alternative_names.csv",
                    help='Name of output csv file')
args = parser.parse_args()

FILENAME_WIKI_DICT = args.wiki_dictionary
#FILENAME_WIKI_DICT = "wiki"
#FILENAME_WIKI ="enwiki-20191001-pages-articles.xml.part01"
OUTPUT_FILE = args.output



ENCODING = "utf-8"

title = None
data = {}


def strip_tag_name( t):
    idx = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t
def clean_paranthesis(text):
    text = text.replace("[[", "]]").replace("]]", "")
    text = text.replace(")","(").replace("(","")
    text = re.sub(r"{{.*}}", "", text)
    text = re.sub(r"<.*>", "", text)
    text = text.replace("''",'"').replace('"',"")
    return text
acceptable_structures = ["| other_names      =","| alias               =","| aka          =","|other_name             =",
                         "| alternate_names     =","| alternate_name =","|other_name             =","|alt_name   ="
                         ]

print("Alternative names searching...")
start = time.time()
for i in os.listdir(FILENAME_WIKI_DICT):
    filename = os.path.join(FILENAME_WIKI_DICT,i)
    for event, elem in etree.iterparse(filename, events=('start', 'end')):
        tname = strip_tag_name(elem.tag)
        if event == 'start':
            if tname == 'page':
                title = ''
                redirect = ''
            elif tname == 'title':
                if elem.text is not None:
                    title = elem.text.replace("'","")
                    print("Title:",title)
        elif event == "end" and tname == "text":  # Get text
            if elem.text is not None and "{{Infobox" in elem.text :
                #print("Bulunan",title)
                found=False
                alternative_names = []
                for struct in acceptable_structures:
                    fields = elem.text.split(struct)
                    if len(fields) > 1:
                        res = fields[1].split("| ")[0]
                        if "{{flatlist|" in res:
                            for i in res.split("\n"):
                                if "* " in i:
                                    res = clean_paranthesis(i.split("* ")[1])
                                    found = True
                                    alternative_names = alternative_names + res.split(",")
                        else:
                            res = fields[1].split("\n")[0].strip()
                            if res != "":
                                res= clean_paranthesis(res)
                                found=True
                                alternative_names = alternative_names + res.replace("&lt;br /&gt;",",").split(",")
                if found:
                    if title == 'Abydos':
                        a = 1

                    alternative_names = [ i.replace(';','').replace('(','').replace(')','') for i in alternative_names]
                    data[title] = "|".join(list(set(alternative_names)))
                    #print(data[title])
        elem.clear()

print("Results are saving.")
with open(OUTPUT_FILE,"w",encoding="utf-8") as fp:
    fp.write("title,alternative_names\n")
    for key,value in tqdm(data.items()):
        fp.write(key+"###"+value+"\n")
end= time.time()
print("Total time:",str(end-start))
with open("Total_time_alternative_names.txt","w") as fp:
    fp.write("Total time:"+str(end-start))
print("Finished")
