import glob
from operator import is_not
import os
import json
import random
import time
import sys
import logging
from moviepy.editor import VideoFileClip

MSASL_DATA_PATH = "C:/Users/user/Documents/GitHub/msasl-video-downloader/wlasl/WLASL/start_kit/MS-ASL"
MY_CLASS = ['black', 'book', 'cousin', 'deaf', 'drink', 'go', 'no', 'orange', 'walk', 'woman']
TRAIN = "MSASL_train.json"
VAL = "MSASL_val.json"
TEST = "MSASL_test.json"

st_time = int(time.time())
logging.basicConfig(filename=f'{MSASL_DATA_PATH}/log/{st_time}.log', filemode='w', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def how_many_class():

    MSASL_classes = json.load(open(os.path.join(MSASL_DATA_PATH, "MSASL_classes.json"), 'r'))
    print("class counts: ", len(MSASL_classes))

    for i in MY_CLASS:
        if i in MSASL_classes:
            print(f'"{i}"', "in MSASL class")


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

def is_not_dir_mkdir(dir_path):
    if os.path.isdir(dir_path):
        logging.info(f"dir is exist: {dir_path}")
    else:
        os.mkdir(dir_path)
        logging.info(f"made dir: {dir_path}")

def mk_dataset_dir(): #dataset directory
    is_not_dir_mkdir(os.path.join(MSASL_DATA_PATH , "dataset"))
    is_not_dir_mkdir(os.path.join(MSASL_DATA_PATH,"dataset","origin"))
    for _type in ['train','test','val']:
        is_not_dir_mkdir(os.path.join(MSASL_DATA_PATH, "dataset",_type))
        for gloss in MY_CLASS:
            is_not_dir_mkdir(os.path.join(MSASL_DATA_PATH, "dataset",_type, gloss))

def download_video_data():

    mk_dataset_dir() # mkdir dataset

    for data,_type in zip([TRAIN,TEST,VAL],['train','test','val']):

        for j in json.load(open(os.path.join(MSASL_DATA_PATH , data) , 'r')):
            gloss = j['clean_text']
            if gloss not in MY_CLASS: continue
            
            
            #origin vid first download
            origin_saveto = os.path.join(MSASL_DATA_PATH, "dataset", "origin")

            origin_vid_name = os.path.join(origin_saveto, j['url'][-11:] + ".mp4")
            if not os.path.exists(origin_vid_name):
                dl_start = time.time()
                rv = youtube_download(j['url'], origin_vid_name)
                
                if not rv:
                    logging.info(f'YouTube origin video {origin_vid_name} downloaded')
                    logging.info(f"YouTube Downloading time: {time.time() - dl_start}")
                else: #youtube download error
                    continue

            else: # if origin vid already downloaded
                logging.error(f"Youtube origin video already exist")
                logging.error(f"url is {j['url']}")
                pass

            #1. video trim and save
            trimvid_saveto = uniquify(os.path.join(MSASL_DATA_PATH, "dataset", _type, gloss , j['url'][-11:] + ".mp4"))
            try:
                clip = VideoFileClip(origin_vid_name)
                clip = clip.subclip(j['start_time'],j['end_time'])
                clip.write_videofile(trimvid_saveto)
                #ffmpeg_extract_subclip(origin_vid_name, j['start_time'],j['end_time'], trimvid_saveto) #origin vid trim
                logging.info(f"video trimmed, video: {origin_vid_name}")
                logging.info(f"TRIM start_time: {j['start_time']}, end_time: {j['end_time']}")

            except Exception:
                logging.error(f"Video Trim error")
                logging.error(f"origin name: {origin_vid_name}")
                logging.error(f"start_time: {j['start_time']}, end_time: {j['end_time']}")

def youtube_download(url, saveto):
    cmd = 'youtube-dl "{}" -o "{}"'.format(url, saveto)
    rv = os.system(cmd)

    if not rv: # rv = 0 means success
        logging.info('Finish downloading youtube video url {}'.format(url))
    else: # rv = 1 means failure
        logging.error('Unsuccessful downloading - youtube video url {}'.format(url))

    time.sleep(random.uniform(1.0, 1.5))

    return rv

def uniquify(path):
    filename, extension = os.path.splitext(path)

    counter = 1
    path = filename + " (" + str(counter) + ")" + extension

    while os.path.exists(path):
        counter += 1
        path = filename + " (" + str(counter) + ")" + extension

    return path


if __name__ == "__main__":
    download_video_data()
    
    logging.info(f"running time: {time.time()-st_time}")