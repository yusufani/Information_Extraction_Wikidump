# Information_Extraction_Wikidump
 

== Information Extraction from Text (entity_kb_english3) ==
<!-- Začátek automaticky generované sekce --><!-- ID: 1095 -->

----
<!-- Konec automaticky generované sekce --><nowiki>Insert non-formatted text here</nowiki>__NOTITLE____NOTOC__

== Information Extraction from Text (entity_kb_english3) ==
<!-- Začátek automaticky generované sekce --><!-- ID: 1095 -->


In this project, it is aimed to extract meaningful information from the dumped wikipedia data.

===Project folder===

/mnt/data/nlp/projects/entity_kb_english3


----

'''REQUIREMENTS'''
* spacy 
* tqdm 
* pandas
* WikiExtractor


----

'''USAGE
'''
# Step -1:  Processing Dump File 

The Wikipedia markdown language is highly detailed and complex. That's why I used the Wikiextractor library to convert this complex language into text.

Syntax:

python -m wikiextractor.WikiExtractor --bytes 1000G --output - <Wikipedia dump file>   > <output_name>

Example:
python -m wikiextractor.WikiExtractor --bytes 1000G --output - /mnt/minerva1/nlp/corpora_datasets/monolingual/english/wikipedia/enwiki-20210101-pages-articles.xml > text_extracted_by_wikiextractor_from_enwiki-20210101-pages-articles.txt

----

This python script will extract files into text folder. This process takes about 68 minutes. After that we can start our main python script which is finds most of the information.

We have 6 main fields in output files which are "title", "alternative_names" , "first_sentence" , "defining_phrases" , "defining_words" and 'nationality'

"title" : Title of the page.

"alternative_names" : "extract_title_first_phrases_words.py" script finds some pre-defined structures("is","was","are","be","stands for","refers to","refer to") in in first paragraph of page. By looking at the sentences that come after these patterns with the help of spacy, script record the appropriate ones as alternative names. Note: a separate Python script had to be used for alternative names from the infobox because there is no option to save the infoboxes in Wikiextractor library.

"first_sentence": First sentence of page.

"defining_phrases" : With the help of spacy, extract phrases after the defining words like "is", "are" etc. 

"defining_words" : With the help of spacy, extract words after the defining words like "is", "are" etc. 

"nationality" : With the help of spacy, extracts nation from defining_phrases and words. Example : American music artist > American

This process takes 28 hours.

Syntax:
 python 1_1_extract_title_first_phrases_words.py --input < Path of Wikipedia file >  --output <Output name of csv file>
Example:
 python 1_1_extract_title_first_phrases_words.py --input /mnt/minerva1/nlp/corpora_datasets/monolingual/english/wikipedia/text_extracted_by_wikiextractor_from_enwiki-20210101-pages-articles.txt  --output  datas/enwiki-20200901-pages-articles_title_first_phrases_words.tsv


----

Although Wikiextractor provides us with regular text data, it is not specialized to hold the infoboxes we use to get alternative names. So we can run the script extract_alternative_names.py at the same time. This python script finds info box and extract acceptable structures from them.

acceptable_structures = 'other_names','alias','aka','other_name','alternate_names','alternate_name','other_name','alt_name'

This process takes 32 minutes.              
Syntax:
 python 1_2_extract_alternative_names.py --wiki_dictionary < Path of Wikipedia file dict. My dump file split into parts so I gave folder path>  --output <Output name of csv file>
Example:
 python 1_2_extract_alternative_names.py --wiki_dictionary /mnt/data/nlp/corpora_datasets/monolingual/english/wikipedia/split_enwiki-20191001-pages-articles  --output datas/enwiki-20200901-pages-articles_alternative_names.csv

----
# Step -2:  Merging dump Files

End of the upper process we need just merge 2 output files by following script. This process takes 16 minutes.

Syntax:
 python 2_1_merge_results.py --alternative_names <Path of alternative names > --main_tsv <Path of main tsv file> --output <path of final output file>
Example:
 python merge_results.py --alternative_names datas/enwiki-20200901-pages-articles_alternative_names.csv --main_tsv datas/enwiki-20200901-pages-articles_title_first_phrases_words.tsv --output datas/enwiki-20200901-pages-articles_merged.tsv

----
# Step -3:  Adding Wikidata Labels and Comparision with wikidata label

For adding Yago and KBpedia classes we need to add wikidata labels. We can take this labels from wikidata. 

In addition of that We also need to show how compatible phrases,words,nationality with the wikidata data. 
The wikidata words are taken from the P106 tags. Before showing results I need to explain all results.

Number of title found : Some of titles are not in dump file. This title shows number of found titles.
Number of extracted words from wikidata : P106 tags can have more than one words. Example P106 = "American musician" - "Actor" . This title shows Total how many sentences in found P106. In this case it is 2.
EXACT True Words: Accuracy: This title shows how many P106 tags and processed words are exactly same. Accuracy calculated from (EXACT True Words/ Number of extracted words from wikidata)
EXACT True Phrases Accuracy:  This title shows how many P106 tags and processed phrases are exactly same. Accuracy calculated from (EXACT True Phrases/ Number of extracted words from wikidata)
EXACT True Nation  Accuracy:  This title shows how many P106 tags and processed nationality are exactly same. Accuracy calculated from (EXACT True Nation/ Number of extracted words from wikidata)
EXACT True Words or Phrases or nationality: 18467 Accuracy: This title shows how many P106 tags and processed words or phrases or nationlity are exactly same. Basically I have merged  words,phrases and nationlity and compare with P106 Tags.  Accuracy calculated from (EXACT True Words or Phrases or nationality/ Number of extracted words from wikidata)


In addition, I calculated how many of the found fields are part of the P106 Tag for a more detailed look. 

For example:
P106 Words= ['a b', 'c']

words = ['a' , 'c' ] 

There is 2 sentence in P106.

'c' value 's Exact same also part of P106 words. Same calculations as in the above section(EXACT MATCHES).

'a' is a part of 'a b' so in this case we mark this case as a match.

For this example Accuracy is 2/2 = 1

PART OF True Words: Accuracy: This title shows how many processed words are part of P106 tags. Accuracy calculated from (PART OF True Words/ Number of extracted words from wikidata)
PART OF True Phrases Accuracy:  This title shows how many processed phrases are part of P106 tags. Accuracy calculated from (PART OFTrue Phrases/ Number of extracted words from wikidata)
PART OF True Nation  Accuracy:  This title shows how many processed nationality are part of P106 tags. Accuracy calculated from (PART OFTrue Nation/ Number of extracted words from wikidata)
PART OF True Words or Phrases or nationality: 18467 Accuracy: This title shows how many processed words, phrases,nationality are part of P106 tags. Basically I have merged words, phrases, nationality and compare them with P106 Tags.  Accuracy calculated from (EXACT True Words or Phrases or nationality/ Number of extracted words from wikidata)


RESULTS:
I will add results when process finished.

Syntax:
 python 3_1_add_wikidata_labels_and_compare.py --wikidata <Wikidata file> --enwikidata <Merged tsv file> --output_log <For logging not important> --output_file <output name>
Example:
 python 3_1_add_wikidata_labels_and_compare.py --wikidata datas/wikidata-20201214-all-BETA.nt.qldwaiso.in_en_wikipedia --enwikidata datas/enwiki-20200901-pages-articles_merged.tsv --output_log datas/wikidata_comparision.txt --output_file datas/enwiki-20200901-pages-articles_wikidata_labeled.tsv



# Step -4:  Adding YAGO and KBpedia 
As the last step, I have added class links from YAGO and KBpedia. For mapping titles I have used wikidata labels from step-3.


Syntax:
 python 4_1_add_classes.py --yago <Yago same as file> --kbpedia <KBpedia wikidata csv file> --enwikidata <Labeled tsv file> --output_file <output file name >
Example:
 python 4_1_add_classes.py --yago datas/yago-wd-sameAs.nt --kbpedia datas/wikidata.csv --enwikidata datas/enwiki-20200901-pages-articles_wikidata_labeled.tsv --output_file datas/enwiki-20200901-pages-articles_out.tsv
