#coding=utf-8
import os
import shutil

list = os.listdir('./')
now = os.getcwd()


for each in list:
    path = os.path.join(now,each)
    if os.path.isdir(path):
        imgs = os.listdir(path)
        for img in imgs:
            imgpath = os.path.join(path,img)
            shutil.copy(imgpath,'../文章图片')
