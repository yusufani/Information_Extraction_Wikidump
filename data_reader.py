import json
import os

FLAG = True

def read_all_files(path, files):
    for file in os.listdir(path):

        new_path = os.path.join(path, file)
        if file.startswith("wiki_"):
            files.append(new_path)
        else:
            files = read_all_files(new_path, files)
    return files


def read_from_multiple_files(all_datas):

    for i in all_datas:
        yield read_file(i)



def read_from_single_file(f,batch_size):
    lines = ''
    print('lines' , lines)
    count = 0
    while True:
        line = f.readline()
        # print(line)
        if line != '':
            if count < batch_size:
                lines += line
                count += 1
            else:
                lines += line
                if line == '</doc>\n':
                    print(50 * '*')
                    print('girdik')
                    print(50 * '*')
                    count = 0
                    res = lines
                    lines =''
                    yield res
        else:
            f.close()
            break


def read_file(path):
    print("File : ", path)
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read()
    return lines
