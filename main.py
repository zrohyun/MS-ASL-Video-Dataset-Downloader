import glob
from operator import is_not
import os
import json
import random
import time
import sys
import logging
from .check_data import uniquify
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


logging.basicConfig(filename=f'{MSASL_DATA_PATH}/log/download_{int(time.time())}.log', filemode='w', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


#import constant
from .check_data import MSASL_DATA_PATH, TEST, VAL, TRAIN, MY_CLASS

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
            if gloss not in MY_CLASS: continue # restrict the class
            
            
            #origin vid first download
            origin_saveto = os.path.join(MSASL_DATA_PATH, "dataset","origin",j['url'][-11:] + ".mp4")

            if not os.path.exists(origin_saveto):
                dl_start = time.time()
                rv = youtube_download(j['url'], origin_saveto)
                
                if not rv:
                    logging.info(f'YouTube origin video {origin_saveto} downloaded')
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
                ffmpeg_extract_subclip(origin_saveto, j['start_time'],j['end_time'], trimvid_saveto) #origin vid trim
                logging.info(f"video trimmed, video: {origin_saveto}")
                logging.info(f"TRIM start_time: {j['start_time']}, end_time: {j['end_time']}")

            except Exception:
                logging.error(f"Video Trim error")
                logging.error(f"origin name: {origin_saveto}")
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




if __name__ == "__main__":
    st_time = time.time()
    download_video_data()
    
    logging.info(f"running time: {time.time()-st_time}")