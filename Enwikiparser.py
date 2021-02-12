import re
import spacy
import csv
from collections import Counter
from string import punctuation


class Parser():
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.defining_words = ("is", "was", "are", "be", "stands for", "refers to", "refer to")

    def split_pages(self, text):
        return text.split("</doc>\n")

    def get_informations(self, page):
        fields = page.split("\n")
        fields = [i for i in fields if i != '' and i != ' ']  # Delete unnecessary empty lines
        title = fields[1]
        # print(fields)
        if len(fields) < 4:
            return False, False, False, False, False , False  # Empty title
        # annotations = self.get_annotations(fields[3])
        first_paragraph = self.get_first_paragraph(fields[2])
        first_paragraph = re.sub(r'\([^)]*\)', '', first_paragraph)
        first_paragraph = self.clean_text(first_paragraph)
        first_sentence = self.get_first_sentence(first_paragraph)
        # print(first_sentence)
        words, phrases = self.get_phrases_and_words(first_paragraph)
        alternative_names = self.get_alternative_names(first_sentence)
        nationality = self.get_nationality(phrases)
        # print(3*"\n")
        # print("Alternative names",alternative_names)
        return title, alternative_names, first_sentence, phrases, words, nationality

    def get_phrases_and_words(self, text):
        doc = self.nlp(text)
        if self.is_definig_sentence(text):
            start_idx = self.get_next_word_idx_after_defining_word(doc)
        else:
            start_idx = 0
        defining_phrases = []
        defining_words = []
        acceptable_poses = (
        "ADJ", "PROPN", "SYM", "NUM", "DET")  # Ofcourse we will take nouns to but in different if statements
        stop_poses = ("VERB", "ADP")
        for idx, tok in enumerate(doc[start_idx:]):
            word = str(tok)
            if word == ".":
                break
            elif tok.pos_ in acceptable_poses:
                if not (idx == 0 and tok.pos_ == "DET"):  # Do not take first DET
                    defining_phrases.append({word: tok.pos_})
            elif tok.pos_ == "NOUN":
                defining_phrases.append({word: tok.pos_})
                defining_words.append({word: tok.pos_})
            elif tok.pos_ == "PUNCT" or tok.pos_ == "CCONJ":
                defining_phrases.append({"|": "SEP"})
                defining_words.append({"|": "SEP"})
            elif tok.pos_ in stop_poses:
                break

        def prepare_strings(data, unique_check=False):
            data_str = ""
            sep = False
            length = len(data)
            for idx, phrase in enumerate(data):
                (word, structure), = phrase.items()
                if structure == "SEP" and sep == True:
                    data_str += "|"
                    sep = False
                elif (idx == length and structure == "ADP") or structure == "DET":
                    pass
                elif structure in acceptable_poses or structure == "NOUN":
                    data_str += word + " "
                    sep = True
            return "|".join(list(set(data_str.split("|")))) if unique_check else data_str

        phrases_str = prepare_strings(defining_phrases)
        words_str = prepare_strings(defining_words, unique_check=True)
        if len(phrases_str) <= 1:
            phrases_str = 'None'
        if len(words_str) <= 1:
            words_str = 'None'

        return words_str, phrases_str

    def save_results(self, OUTPUT_PATH, KEYS, result, first=False):
        try:
            if first:
                with open(OUTPUT_PATH, 'w', encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=KEYS, delimiter='\t')
                    writer.writeheader()
            else:
                with open(OUTPUT_PATH, 'a+', encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=KEYS, delimiter='\t')
                    for data in result:
                        writer.writerow(data)
        except IOError:
            print("I/O error")

    def get_title(self, head):
        return head.split('title=')[1].replace('"', "").replace(">", "")

    def is_definig_sentence(self, sentence):
        return True if any(words in sentence for words in self.defining_words) else False

    '''
    def get_annotations(self,text):
        fields = text.split("<a href=")
        annotations = []
        for word  in fields:
            if ">" in word:
                annotations.append(word.split(">")[1].split("</")[0])
        return annotations
    '''

    def get_phrases(self, text):
        doc = self.nlp(text)
        return [chunk.text for chunk in doc.noun_chunks]

        return result

    def get_first_sentence(self, paragraph):
        # print(paragraph)
        sentence = self.nlp(paragraph)
        # Identify the sentences using attribute
        sentences = list(sentence.sents)
        # print(sentences)
        return paragraph.split('\n')[0] if len(sentences) <= 0 else str(sentences[0])

    def get_first_paragraph(self, paragraph):
        paragraphs = self.clean_hypertext(paragraph).split("\n")
        if len(paragraphs) > 1 and paragraphs[0].endswith((":", ";")):
            return self.clean_hypertext(paragraph).split("\n")[0] + self.clean_hypertext(paragraph).split("\n")[1]
        else:
            return paragraphs[0]

    def clean_hypertext(self, text):
        return re.sub(r'<a href="+[A-Za-z0-9%]+">', "", text).replace("</a>", "")

    def get_next_word_idx_after_defining_word(self, doc):
        ":arg:text first paragraph of title"
        "This function finds a first defining word's index and return +1"
        for idx, tok in enumerate(doc):
            word = str(tok)
            if word in self.defining_words:
                return idx + 1

    def get_alternative_names(self, first_paragraph):
        def extract_names(text, searcing_word):
            text = re.sub(r'\([^)]*\)', '', text)
            # print(text)
            doc = self.nlp(text)
            found = False
            alternative_names = []
            acceptable_poses = ("ADJ", "PROPN", "SYM", "NUM", "NOUN", "ADP")
            # print([{str(tok),tok.pos_} for tok in doc ])
            for tok in doc:
                word = str(tok)
                if word == searcing_word:
                    found = True
                elif found:
                    if tok.pos_ in acceptable_poses or word == "-":
                        alternative_names.append(word + " ")
                    elif tok.pos_ == "CCONJ" or word == ",":
                        alternative_names.append("|")
                    elif tok.pos_ == "DET":
                        pass
                    else:
                        break
            result = ""
            sep = False
            for idx, name in enumerate(alternative_names):
                if (idx == 0 and name == "|") or (idx == len(alternative_names) - 1 and name == "|"):
                    pass
                elif name == "|":
                    if sep:
                        result += "|"
                        sep = False
                else:
                    result += name
                    sep = True
            # print(5*"\n")
            # print(text)
            # print(alternative_names)
            # print("Alternative  names:",result)
            return result

        structures = ("known as", "called", ")", "(")
        if any(x in first_paragraph for x in structures):
            if "known as" in first_paragraph:
                # print("Known as detected")
                # print(first_paragraph)
                return extract_names(first_paragraph, "as")
            elif "called" in first_paragraph:

                # print("called  detected")
                # print(first_paragraph)
                return extract_names(first_paragraph, "called")
            else:
                if ")" in first_paragraph and "(" in first_paragraph:
                    fields = first_paragraph.replace(")", "(").split("(")
                    if len(fields[1]) == 1 and fields[1].isupper():
                        return fields[1]
                return ""
        else:
            return "None"

    def clean_text(self, first_sentence):

        first_sentence = first_sentence.replace(';', '').replace('(,', '(').replace('"', '')
        if '(' in first_sentence or ')' in first_sentence:
            typos = ['()', '( )', '( , )', '(,)', '(, )', '( , , )', '("")""', '(  )', '', '(   )', '( ,)']
            for i in typos:
                first_sentence = first_sentence.replace(i, '')
            new_sentence = ''
            search = False
            for i in first_sentence:
                if i == '(':
                    search = True
                    new_sentence += i
                elif search:
                    if (i.isalpha() or i.isdigit()):
                        search = False
                        new_sentence += i
                else:
                    new_sentence += i
            return new_sentence

        return first_sentence

    def get_nationality(self, phrases):
        nations = []
        for i in phrases.split('|'):
            doc = self.nlp(i)
            for ent in doc.ents:
                if ent.label_ == 'NORP':
                    nations.append(ent.text)

        return '|'.join([i.strip() for i in nations]) if len(nations) >= 1 else 'None'


class Enwiki_parser:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')

    def strip_tag_name(self, t):
        idx = t.rfind("}")
        if idx != -1:
            t = t[idx + 1:]
        return t

    def get_structed_data(self):
        data = {}
        data["alternative_names"] = []
        data["first_sentence"] = ""
        data["defining_phrases"] = []
        data["defining_words"] = []
        return data

    def delete_between_paranthesis(self, text):
        return re.sub(r'\([^()]*\)', '', text)

    def check_open_brackets(self, text, idx):
        return text[idx] == "{" and idx + 1 < len(text) and text[idx + 1] == "{"

    def check_close_brackets(self, text, idx):
        return text[idx] == "}" and idx + 1 < len(text) and text[idx + 1] == "}"

    def delete_words_between_curly_brackets(self, text):
        '''
        This function deletes sentences between "{{" and "}}". That format for wikitext. We do not need that info
        '''
        open = 0  # if {{ found +1 , if }} -1
        new_text = ""
        # old_Text = ""
        idx = 0
        while idx < len(text):
            is_curl_bracket = True
            if self.check_open_brackets(text, idx):
                # old_Text+="\n"
                open += 1
                idx += 2
            elif self.check_close_brackets(text, idx):
                open -= 1
                idx += 2
                if idx < len(text) and (text[idx] == "," or text[idx] == ";"):
                    idx += 1
                if self.check_open_brackets(text, idx):  # For }}{{ case
                    open += 1
                    idx += 2
            else:
                is_curl_bracket = False
            if open == 0 and idx < len(text):
                new_text += text[idx]
            '''
            else:
                old_Text+=text[idx]
            '''
            if not is_curl_bracket:
                idx += 1
        text = new_text.strip()  # Delete 1 more whitespaces and \n or \f etc.
        return text

    def get_first_paragraph(self, text, title):
        """
        if "(" in title:  # EXAMPLE : "Animalia (book)": We are looking for '''Animalia''' so delete phrantesis for only searching
            title = self.delete_between_paranthesis(title).strip()
        for parag in text.split("\n"):
            if "'''" + title + "'''" in parag:
                return parag
        raise Exception("not found first paragraph")

        """
        return text.split("\n")[0]

    def delete_meaningless_words(self, text, delete_brackets=True):
        text = self.delete_references(text)
        if delete_brackets:
            text = self.delete_File_bracket(text)
        text = text.replace("&quot;", '"')  # Change quota
        return text

    def get_first_sentence(self, text, prgh_title):
        '''
        :arg
        text: Contains wikipedia dump text .
        :returns
        string : Clean First pharagraph of text.
        '''
        text = self.delete_words_between_curly_brackets(text)
        text = self.get_first_paragraph(text, prgh_title)
        text = self.delete_meaningless_words(text)
        text = text.replace("'''", "").replace("[[", "").replace("]]", "")
        return text.split(".")[0]

    def get_hotwords(self, text):
        result = []
        pos_tag = ['PROPN', 'ADJ', 'NOUN']  # 1
        doc = self.nlp(text.lower())  # 2
        for token in doc:
            # 3
            if (token.text in self.nlp.Defaults.stop_words or token.text in punctuation):
                continue
            # 4
            if (token.pos_ in pos_tag):
                result.append(token.text)

        return result  # 5

    def add_defining_phrases_words(self, text, prgh_title):
        phareses = ""
        words = ""
        text = self.delete_words_between_curly_brackets(text)
        text = self.get_first_paragraph(text, prgh_title)
        text = self.delete_meaningless_words(text, delete_brackets=False)
        fields = text.replace("[[", "]]").split("]]")
        text = self.delete_File_bracket(text)
        doc = self.nlp(text.replace("|", ", "))
        phrases = [chunk.text for chunk in doc.noun_chunks]

        words = self.get_hotwords(text.replace("|", ", "))
        defining_pharases = set()
        defining_words = set()

        # print("words", words)
        # print("Phrases", phareses)
        for idx, val in enumerate(fields):
            if idx % 2 == 1:
                for field in val.split("|"):
                    if field in words:
                        defining_words.add(field)
                    for p in phrases:
                        if val in p:
                            defining_pharases.add(field)
        print("Metin", text)
        print("Defining words", defining_words)
        print("Defining phrases", defining_pharases)
        # print(fields[1:])
        pass

    def delete_references(self, text):
        text = text.replace("<</ref>", "<ref>").split("<ref>")
        new = ""
        for idx, val in enumerate(text):
            if idx % 2 == 0:
                new += val
        return new

    def delete_File_bracket(self, text):
        new_file = ""
        for i in text.replace("]]", "[[").split("[["):
            if "File:" not in i:
                new_file += i + " "

        return new_file
