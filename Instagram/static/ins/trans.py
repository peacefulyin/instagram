import os
import shutil

list = os.listdir('./article_image')
print list
for each in list:
    shortcode = each.split('.')[0]
    print shortcode
    abpath = os.path.abspath(each)
    if not os.path.exists('./images_storage/'+shortcode):
        os.mkdir('./images_storage/'+shortcode)
    shutil.copy('./article_image/'+each,'./images_storage/'+shortcode+'/1.jpg')
    #print os.path.abspath(each)