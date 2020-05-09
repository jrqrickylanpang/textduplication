import os
import re
import shutil
import jieba.posseg
from docx import Document
from simhash import Simhash
from io import open
from io import StringIO
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, process_pdf


def hash_dis(hash_x, hash_y):
    hash_dif = hash_x ^ hash_y
    dis = 0
    while hash_dif > 0:
        dis += 1
        hash_dif &= hash_dif-1
    return dis


def chk_level(dis):
    return 100-dis*2


def chk_hash(hash_code):
    chk_list = []
    for hash_file in hash_list:
        chk_list.append((hash_file[0], chk_level(hash_dis(hash_file[1], hash_code))))
        if chk_list[-1][1] < 60:
            chk_list.pop()
    chk_list.sort(key=lambda s: -s[1])
    return chk_list


def word_weight(word_type):
    word_type = str(word_type)[0]
    type_value = {'n': 4, 'v': 3, 'a': 2}
    if word_type in type_value:
        return type_value[word_type]
    else:
        return 1


def prc_str(file_str):
    file_word = jieba.posseg.cut(file_str)
    word_list = []
    for word in file_word:
        word_list.append((word.word, word_weight(word.flag)))
    return Simhash(word_list).value


def prt_report(file_name):
    real_name = os.path.splitext(file_name)[0]
    with open("report/"+real_name+"_report.txt", "w", encoding="utf-8") as f:
        chk_list = chk_hash(prc_str(get_file_txt("check_join/"+file_name)))
        if len(chk_list) == 0:
            f.write("No identical documents.")
        for chk_msg in chk_list:
            f.write("file <"+chk_msg[0]+"> similarity level: "+str(chk_msg[1])+".\n")


def join_file(file_name):
    real_name = os.path.splitext(file_name)[0]
    hash_list.append((real_name, prc_str(get_file_txt("input_join/"+file_name))))


def find_chinese(file_str):
    pattern = re.compile(r'[^\u4e00-\u9fa5]')
    chinese_str = re.sub(pattern, '', file_str)
    return chinese_str


def get_file_pdf(path):
    with open(path, "rb") as f:
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        process_pdf(rsrcmgr, device, f)
        device.close()
        content = retstr.getvalue()
        retstr.close()
    return content


def get_file_docx(path):
    f = Document(path)
    file_str = []
    for par in f.paragraphs:
        file_str.append(par.text)
    return '\n'.join(file_str)


def get_file_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        file_str = f.read()
    return file_str


def get_file_list(path, config):
    file_list = []
    for file_name in os.listdir(path):
        if os.path.splitext(file_name)[1] == '.'+config:
            file_list.append(os.path.splitext(file_name)[0])
    return file_list


def get_file(path):
    type_list = ["pdf", "docx", "txt"]
    func_list = {"pdf": get_file_pdf, "docx": get_file_docx, "txt": get_file_txt}
    prc_type = {"input": join_file, "check": prt_report}
    cnt = 0
    for file_type in type_list:
        for file_name in get_file_list(path, file_type):
            if not os.path.isfile(path+"_join/"+file_name+".txt"):
                with open(path+"_join/"+file_name+".txt", "w", encoding="utf-8") as f:
                    f.write(find_chinese(func_list[file_type](path+'/'+file_name+'.'+file_type)))
                    os.remove(path+'/'+file_name+'.'+file_type)
                prc_type[path](file_name+".txt")
                cnt += 1
    return cnt


def get_mid():
    if os.path.isfile("mid/name_hash.txt"):
        with open("mid/name_hash.txt", "r", encoding="utf-8") as f:
            origin_list = f.readlines()
            origin_size = len(origin_list)
            for i in range(0, origin_size):
                if i % 2 == 1:
                    hash_list.append((origin_list[i-1].strip('\n'), int(origin_list[i])))
            ard_mid[0] = len(hash_list)


def upd_mid():
    with open("mid/name_hash.txt", "a", encoding="utf-8") as f:
        for i in range(ard_mid[0], len(hash_list)):
            f.write(hash_list[i][0]+'\n'+str(hash_list[i][1])+'\n')
        ard_mid[0] = len(hash_list)


def del_mid():
    del_dir(init_list)
    mk_dir(init_list)
    hash_list.clear()
    ard_mid[0] = 0


def mk_dir(path_list):
    for path in path_list:
        if not os.path.exists(path):
            os.makedirs(path)


def del_dir(path_list):
    for path in path_list:
        if os.path.exists(path):
            shutil.rmtree(path)


def main():
    while True:
        print("Typing character <i> to input files from <input>.")
        print("Typing character <c> to check files from <check>, report will be generated in <report>.")
        print("Typing character <q> to quit program.")
        print("Typing character <r> to reset system.")
        ret = input("Please select a function to execute:\n")
        func_type = {'i': "input", 'c': "check"}
        if ret in func_type:
            print(str(get_file(func_type[ret]))+" files completed.\n\n")
            upd_mid()
        elif ret == 'q':
            break
        elif ret == 'r':
            del_mid()
            print("System reset.\n\n")
        else:
            print("Unknown input, please try again.\n\n")


def init():
    global init_list, hash_list, ard_mid
    init_list = ["input", "input_join", "check", "check_join", "report", "mid"]
    mk_dir(init_list)
    hash_list = []
    ard_mid = [0, ]
    get_mid()


if __name__ == "__main__":
    init()
    main()
