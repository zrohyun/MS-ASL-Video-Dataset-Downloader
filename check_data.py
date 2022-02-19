import json
import os
import logging
import time
import sys


MSASL_DATA_PATH = "C:/Users/user/Documents/GitHub/msasl-video-downloader/wlasl/WLASL/start_kit/MS-ASL"
TRAIN = "MSASL_train.json"
VAL = "MSASL_val.json"
TEST = "MSASL_test.json"
# restrict the class
MY_CLASS = ['black', 'book', 'cousin', 'deaf', 'drink', 'go', 'no', 'orange', 'walk', 'woman']

logging.basicConfig(filename=f'{MSASL_DATA_PATH}/log/checkdata_{int(time.time())}.log', filemode='w', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def how_many_class():

    MSASL_classes = json.load(open(os.path.join(MSASL_DATA_PATH, "MSASL_classes.json"), 'r'))
    print("class counts: ", len(MSASL_classes))

def count_dataset():

    cnt_inval_url = cnt_val_url=0
    for j in [TRAIN,TEST,VAL]:
        a = json.load(open(os.path.join(MSASL_DATA_PATH,j), 'r'))
        count_by_class = {i:0 for i in MY_CLASS}
        for i in a:
            if i['clean_text'] in MY_CLASS:
                count_by_class[i['clean_text']] += 1
                if check_url_valid(i['url']): cnt_val_url+=1
                else: cnt_inval_url += 1
                print(i)

        print(f"{j}:",count_by_class)
        print("val,inval:",cnt_val_url,cnt_inval_url)


def check_url_valid(url = 'https://www.youtube.com'):
    
    try:
        assert ("youtube" in url) or ("youtu.be" in url) , "It's not a youtube url"
        import requests as r

        assert r.get(url).status_code == 200, f"{url} expired"
    except Exception as e:
        logging.error(f"{url} is invalid")
        return False
    
    logging.info(f"{url} is valid")
    
    return True

def uniquify(path):
    filename, extension = os.path.splitext(path)

    counter = 1
    path = filename + " (" + str(counter) + ")" + extension

    while os.path.exists(path):
        counter += 1
        path = filename + " (" + str(counter) + ")" + extension

    return path