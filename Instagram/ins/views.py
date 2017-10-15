#coding=utf-8
import os
import random
import shutil
import subprocess
import time
from datetime import datetime
from hashlib import sha1

from PIL import Image
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from log_setting import logger

from constant import LOGIN_TOKEN
from ins.models import InsArticle, InsUser, InsComment, InsLike, InsFriend, InsSign

from email.mime.text import MIMEText
import smtplib
from email.utils import formataddr
from email.header import Header

import logging
import sys


signup_logger = logger(logname='ins_signup', filename='ins_signup.log', level=logging.INFO)
pub_logger = logger(logname='ins_pub', filename='ins_pub.log', level=logging.INFO)
signin_logger = logger(logname='ins_signin', filename='ins_signin.log', level=logging.INFO)

def veti_logi(f):
    def warp(request, *args):
        username = request.COOKIES.get('islogin')
        origin_token = request.COOKIES.get('token')
        if username:
            token = sha1(LOGIN_TOKEN + username).hexdigest()
            if token == origin_token:
                ret = f(request,*args)
                return ret
        return redirect('/login')
    return warp

def aready_logi(f):
    def warp(request, *args):
        if request.COOKIES.get('islogin'):
            return redirect('/home')
        else:
            ret = f(request, *args)
            return ret
    return warp

def chscale(size, filepath,type):
    width = size[0]
    height = size[1]
    infile = filepath

    outfile = os.path.splitext(infile)[0] + '.' + type

    im = Image.open(infile)
    scale = width / height
    scale_width, scale_height, fi_height, fiwidth = 1, 1, 1, 1
    while scale_width < im.size[0]:
        if scale_height == scale_width / scale:
            fiwidth = scale_width
            fi_height = scale_height
        scale_width += 1
        scale_height = scale_width / scale

    hori, verti = (im.size[0] / 2, im.size[1] / 2)
    box = (hori - fiwidth / 2, verti - fi_height / 2, hori + fiwidth / 2, verti + fi_height / 2)
    region = im.crop(box)

    region.thumbnail((width, height), Image.ANTIALIAS)
    os.remove(infile)
    region.save(outfile)



def index(request):
    articles = InsArticle.objects.order_by('-pub_time')
    pagenator = Paginator(articles,10)
    username = request.COOKIES.get('islogin')

    expore_users = []
    for each in InsUser.objects.raw('select * from ins_user where id in (select distinct user_id from ins_article)'):
        expore_users.append(each)

    def get_random_user():
        random_user = random.sample(expore_users, 3)
        username = request.COOKIES.get('islogin')
        if username:
            user = InsUser.objects.get(username=username)
            if user in random_user:
                get_random_user()
        return random_user

    random_user = get_random_user()

    if username:
        user = InsUser.objects.get(username=username)
        friends = InsFriend.objects.filter(people=user)

        if len(friends) < 4:
            friend_page = friends
        else:
            friend_page = random.sample(friends,4)


        context = {'page':pagenator.page(1), 'username':username, 'friend_page': friend_page, 'random_user':random_user}

    else:
        context = {'page': pagenator.page(1), 'random_user': random_user}



    return render(request, 'ins/index.html', context)



def recently(request):
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)
    sign_list = InsSign.objects.filter(target=user).order_by('-pub_time')
    sign_list = [{'username':each.people.username, 'pub_time':each.pub_time, 'shortcode': each.article.shortcode} for each in sign_list]
    for each in sign_list:
        print each['username']
    context = {'list':sign_list}

    return JsonResponse(context)



@aready_logi
def login(request):
    return render(request, 'ins/login.html')



@veti_logi
def edit(request):
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)
    context = {'user': user}
    return render(request, 'ins/edit.html', context)

@veti_logi
def chpass(request):
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)
    context = {'user': user}
    return render(request, 'ins/chpass.html', context)

def chpass_backend(request):
    print 'hahaha'
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)

    true_password = user.password
    origin_pass = request.POST.get('origin_pass')
    new_pass = request.POST.get('new_pass')
    confirm_pass = request.POST.get('confirm_pass')

    if origin_pass != true_password:
        return JsonResponse({'false':'密码错误'})

    user.password = new_pass
    user.save()
    return JsonResponse({'true':'密码更改成功'})

def reset_pass(request):
    return render(request, 'ins/resetpass.html')




@veti_logi
def manage_access(request):
    return render(request, 'ins/manage_access.html')

@veti_logi
def comment_filter(request):
    return render(request, 'ins/comment_filter.html')

@veti_logi
def email_set(request):
    return render(request, 'ins/email_set.html')

@veti_logi
def contact_history(request):
    return render(request, 'ins/contact_history.html')

@veti_logi
def home(request):
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)
    articles = user.insarticle_set.order_by('-pub_time')
    paginator = Paginator(articles, 12)
    page = paginator.page(1)
    artical_total = len(articles)

    follow = InsFriend.objects.filter(people=user)
    follower = InsFriend.objects.filter(target=user)

    follow = [each.target for each in follow]
    follower = [each.people for each in follower]

    context = {'articles':page, 'user':user,'artical_total':artical_total, 'follow':follow, 'follower':follower}

    return render(request, 'ins/home.html', context)


def explore_people(request):
    expore_users = []
    for each in InsUser.objects.raw('select * from ins_user where id in (select distinct user_id from ins_article)'):
        expore_users.append(each)

    def get_random_user():
        random_user = random.sample(expore_users,12)
        username = request.COOKIES.get('islogin')
        if username:
            user = InsUser.objects.get(username=username)
            if user in random_user:
                get_random_user()
        return random_user

    random_user = get_random_user()

    context = {'users':random_user}
    return render(request, 'ins/explore_people.html', context)

def explore(request):
    articles = InsArticle.objects.order_by('-pub_time')
    paginator = Paginator(articles, 24)

    expore_users = []
    for each in InsUser.objects.raw('select * from ins_user where id in (select distinct user_id from ins_article)'):
        expore_users.append(each)

    def get_random_user():
        random_user = random.sample(expore_users, 3)
        username = request.COOKIES.get('islogin')
        if username:
            user = InsUser.objects.get(username=username)
            if user in random_user:
                get_random_user()
        return random_user

    random_user = get_random_user()


    context = {'page': paginator.page(1), 'random_user':random_user}

    return render(request, 'ins/explore.html', context)

def qweasd(request, pagenum):
    print pagenum

    articles = InsArticle.objects.all()
    paginator = Paginator(articles, 10)
    if int(pagenum) <= paginator.num_pages:
        page = paginator.page(int(pagenum))
        tem_list = []
        for each in page:
            user = each.user
            dict = model_to_dict(each)
            dict['user'] = model_to_dict(user)
            likenum = len(InsLike.objects.filter(article=each))
            dict['likenum'] = likenum

            allcomments = each.inscomment_set.order_by('-pub_time')
            comments = []
            for comment in allcomments:
                comment_username = comment.user.username
                comment_dict = model_to_dict(comment)
                comment_dict.setdefault('username',comment_username)
                comments.append(comment_dict)
            dict['comments'] = comments

            login_username = request.COOKIES.get('islogin')
            if login_username:
                login_user = InsUser.objects.get(username=login_username)
                object_like = InsLike.objects.filter(user=login_user,article=each)
                if object_like:
                    dict['islike'] = 'true'
                else:
                    dict['islike'] = 'false'

            if dict['type'] == 'image':
                path = 'static/ins/images_storage/' + dict['shortcode']
            else:
                path = 'static/ins/videos_storage/' + dict['shortcode']
            img_total = len(os.listdir(path))
            dict['img_total'] = img_total
            tem_list.append(dict)
        return JsonResponse({'page': tem_list, 'empty': 'false'})

    else:
        return JsonResponse({'empty': 'true'})

def explore_more(request, pagenum):
    articles = InsArticle.objects.all().order_by('-pub_time')
    paginator = Paginator(articles, 24)
    if int(pagenum) <= paginator.num_pages:
        page = paginator.page(int(pagenum))
        list = [model_to_dict(each) for each in page]
        tem_list = []
        for each in list:
            path = 'static/ins/images_storage/' + each['shortcode']
            img_total = len(os.listdir(path))
            each.setdefault('img_total',img_total)
            tem_list.append(each)
        list = tem_list
        return JsonResponse({'page': list,'empty': 'false'})

    else:
        return JsonResponse({'empty': 'true'})

def blog(request, username):
    try:
        login_user = request.COOKIES.get('islogin')
    except:
        login_user = False
    if username == login_user:
       return redirect('/home')
    user = InsUser.objects.get(username=username)
    articles = user.insarticle_set.order_by('-pub_time')
    paginator = Paginator(articles, 12)
    page = paginator.page(1)
    artical_total = len(articles)

    follow = InsFriend.objects.filter(people=user)
    follower = InsFriend.objects.filter(target=user)

    follow = [each.target for each in follow]
    follower = [each.people for each in follower]

    context = {'articles':page,'user':user, 'artical_total':artical_total, 'follow':follow, 'follower':follower}
    return render(request, 'ins/blog.html',context)


def blog_more(request, username, pagenum):
    user = InsUser.objects.get(username=username)
    articles = user.insarticle_set.all().order_by('-pub_time')
    paginator = Paginator(articles, 12)
    if int(pagenum) < paginator.num_pages:
        page = paginator.page(int(pagenum))
        list = [model_to_dict(each) for each in page]
        return JsonResponse({'page': list,'empty': 'false'})

    elif int(pagenum) == paginator.num_pages:
        page = paginator.page(int(pagenum))
        list = [model_to_dict(each) for each in page]
        return JsonResponse({'page': list, 'empty': 'true'})




def signin(request):
    name = request.POST.get('name')
    password = request.POST.get('password')
    token = sha1(LOGIN_TOKEN+name).hexdigest()

    if '@' in name:
        try:
            user = InsUser.objects.get(email=name)
        except:
            user = False
    else:
        try:
            user = InsUser.objects.get(username=name)
        except:
            user = False

    if not user:
        return JsonResponse({'false':'用户名或邮箱错误'})

    truepwd = user.password
    if password != truepwd:
        return  JsonResponse({'false':'密码错误'})

    response = JsonResponse({'true':'登录成功'})
    request.session['islogin'] = user.username
    response.set_cookie('islogin', user.username)
    response.set_cookie('token', token)

    log_info = 'username:{}'.format(name)
    signin_logger.info(log_info)
    return response

def signup(request):
    email = request.POST.get('email')
    full_name = request.POST.get('full_name')
    username = request.POST.get('username')
    password = request.POST.get('password')


    find_user = InsUser.objects.filter(username=username)
    if find_user:
        return JsonResponse({'false': '用户名已存在'})

    find_email = InsUser.objects.filter(email=email)
    if find_email:
        return JsonResponse({'false': '邮箱已被注册'})


    if email and full_name and username and password:

        user = InsUser()
        user.username = username
        user.full_name = full_name
        user.password = password
        user.email = email
        try:
            user.save()
        except:
            return JsonResponse({'false':'fail to regi'})

    log_info = 'username:{}, email:{}'.format(username, email)
    signup_logger.info(log_info)
    return JsonResponse({'true': '注册成功'})


def veri_email(request, email):
    if '@' in email:
        try:
            user = InsUser.objects.get(email=email)
        except:
            user = False
    else:
        try:
            user = InsUser.objects.get(username=email)
        except:
            user = False

    if user:
        return JsonResponse({'true':'账户已经存在','email':user.email})

    return JsonResponse({'false': '用户名或邮箱错误'})

def release(request):
    response = JsonResponse({'true':''})
    response.delete_cookie('islogin')
    request.session['islogin'] = ''
    return response


def explore_search(request, keyword):
    users = InsUser.objects.filter(username__icontains=keyword)
    login_username = request.COOKIES.get('islogin')

    page = [model_to_dict(each) for each in Paginator(users,20).page(1) if each.username != login_username]
    if page:
        context = {'page':page, 'true':'has result'}
    else:
        context = {'page': page, 'false': 'not found'}
    return JsonResponse(context)



def signfriend(request, keyword):
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)
    friends = InsFriend.objects.filter(people=user)
    filter_list = []
    for each in friends:
        if keyword in each.target.username:
            filter_list.append({'username':each.target.username, 'full_name': each.target.full_name, 'id': each.target.id})

    if filter_list:
        context = {'list':filter_list, 'true':'has result'}
    else:
        context = {'false': 'not found'}

    return JsonResponse(context)


def addsign(request):
    login_username = request.COOKIES.get('islogin')
    target_username = request.POST.get('username')
    shortcode = request.POST.get('shortcode')

    user = InsUser.objects.get(username=login_username)
    target = InsUser.objects.get(username=target_username)
    article = InsArticle.objects.get(shortcode=shortcode)

    time = timezone.now()

    try:
        object_sign = InsSign()
        object_sign.people = user
        object_sign.target = target
        object_sign.article = article
        object_sign.pub_time = time
        object_sign.save()
        return JsonResponse({'true':'add sign success'})
    except:
        return JsonResponse({'false': 'add sign failure'})




def sendContent(request, shortcode):
    article = InsArticle.objects.get(shortcode=shortcode)
    return JsonResponse({'content':article.text})


def show_detail(request, shortcode, pagenum):


    article = InsArticle.objects.get(shortcode=shortcode)
    comments = article.inscomment_set.order_by('-pub_time')
    target_username = article.user.username

    login_username = request.COOKIES.get('islogin')
    login_user = InsUser.objects.get(username=login_username)
    targetuser = InsUser.objects.get(username=target_username)
    friend = InsFriend.objects.filter(people=login_user,target=targetuser)
    isfriend = 'true' if friend else 'false'

    like = InsLike.objects.filter(user=login_user, article=article)
    islike = 'true' if like else 'false'

    filepath = 'static/ins/images_storage/' + shortcode
    images = os.listdir(filepath)


    paginator = Paginator(comments, 21)
    if int(pagenum)  <= paginator.num_pages:
        page = paginator.page(pagenum)
        list = [{'content':each.content,'username':each.user.username, 'id':each.id} for each in page]

        article = model_to_dict(article)
        context = {'page': list,'article':article,'username':target_username, 'isfriend':isfriend, 'islike':islike, 'img_total':len(images)}

        if int(pagenum) == paginator.num_pages:
            context.setdefault('empty','true')
        return JsonResponse(context)
    else:
        return JsonResponse({'empty':'true'})



def sendComment(request, shortcode, pagenum):
    article = InsArticle.objects.get(shortcode=shortcode)
    comments = article.inscomment_set.order_by('-pub_time')
    paginator = Paginator(comments,21)
    if int(pagenum)  <= paginator.num_pages:
        page = paginator.page(pagenum)
        list = [{'content':each.content,'username':each.user.username, 'id':each.id} for each in page]
        context = {'page': list}

        if int(pagenum) == paginator.num_pages:
            context.setdefault('empty','true')
        return JsonResponse(context)
    else:
        return JsonResponse({'empty':'true'})

def index_sendComment(request, shortcode, pagenum):
    article = InsArticle.objects.get(shortcode=shortcode)
    comments = article.inscomment_set.order_by('-pub_time')
    paginator = Paginator(comments,5)
    if int(pagenum)  <= paginator.num_pages:

        page = paginator.page(pagenum)
        list = [{'content':each.content,'username':each.user.username, 'id': each.id} for each in page]

        context = {'page': list}
        if int(pagenum) == paginator.num_pages:
            context.setdefault('empty','true')
        return JsonResponse(context)
    else:
        return JsonResponse({'empty':'true'})


def leave_comment(request):
    content = request.POST.get('content')
    sign_string = request.POST.get('sign_string')
    shortcode = request.POST.get('shortcode')
    article = InsArticle.objects.get(shortcode=shortcode)
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)
    time = timezone.now()

    try:
        object_comment = InsComment()
        object_comment.pub_time = time
        object_comment.content = content + ' ' + sign_string
        object_comment.article = article
        object_comment.user = user
        object_comment.save()
    except:
        return JsonResponse('false','can,t do it')



    if sign_string:
        signlist = sign_string.split('@')[1:]
        for target_username in signlist:
            try:
                object_sign = InsSign()
                object_sign.people = user
                target = InsUser.objects.get(username=target_username)
                object_sign.target = target
                object_sign.article = article
                object_sign.pub_time = time
                object_sign.save()
            except:
                return JsonResponse({'false': 'add sign failure'})

    return JsonResponse({'true':'leave comment success'})


def delete_comment(request, comment_id):
    username = request.COOKIES.get('islogin')
    login_user = InsUser.objects.get(username=username)
    comment = InsComment.objects.get(id=comment_id)
    if comment.user == login_user:
        comment.delete()
        return JsonResponse({'true':'comment_delete_over'})
    else:
        return JsonResponse({'false':'bad guy!'})


def add_like(request, shortcode):
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)
    article = InsArticle.objects.get(shortcode=shortcode)
    try:
        object_like = InsLike()
        object_like.user = user
        object_like.article = article
        object_like.save()
        return JsonResponse({'result': 'ok'})
    except:
        return JsonResponse({'result': 'wrong'})


def remove_like(request, shortcode):
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)
    article = InsArticle.objects.get(shortcode=shortcode)
    try:
        object_like = InsLike.objects.filter(user=user,article=article)
        for each in object_like:
            each.delete()
        return JsonResponse({'result': 'ok'})
    except:
        return JsonResponse({'result':'wrong'})

def add_follow(request, target_full_name):
    username = request.COOKIES.get('islogin')
    people = InsUser.objects.get(username=username)
    target = InsUser.objects.get(full_name=target_full_name)
    object_friend = InsFriend.objects.filter(people=people, target=target)
    if not object_friend:
        try:
            object_friend = InsFriend()
            object_friend.people = people
            object_friend.target = target
            object_friend.save()
            return JsonResponse({'result': 'ok'})
        except:
            return JsonResponse({'result': 'wrong'})
    return JsonResponse({'result': 'ok'})

def remove_follow(request, target_full_name):
    username = request.COOKIES.get('islogin')
    people = InsUser.objects.get(username=username)
    target = InsUser.objects.get(full_name=target_full_name)

    object_friend = InsFriend.objects.filter(people=people,target=target)
    for each in object_friend:
        each.delete()
    return JsonResponse({'result': 'ok'})



def upfile(request):
    if request.method == 'POST':
        shortcode =  request.POST.get('shortcode')
        mediatype = request.POST.get('mediatype')

        if mediatype == 'image':
            path = 'static/ins/images_storage_temp/' + shortcode

            if not os.path.exists(path):
                os.mkdir(path)

            file = request.FILES['upfile']

            if not file:
                return JsonResponse({'false':'upload fail'})

            imglist = os.listdir(path)
            if imglist:
                maxnum = 1
                for each in imglist:
                    if each.endswith('.jpg'):
                        num = int(each.split('.')[0])
                        maxnum = num if num > maxnum else maxnum
                        filenum = maxnum + 1
            else:
                filenum = 1

            tail = str(file).split('.').pop()
            fullpath = os.path.join(path,str(filenum)+'.'+tail)
            outfullpath = fullpath.replace(tail,'jpg')

            with open(fullpath,'wb') as f:
                while True:
                    chunk = file.read(512)
                    if chunk:
                        f.write(chunk)
                    else:
                        break
            if fullpath != outfullpath:
                try:
                    Image.open(fullpath).save(outfullpath)
                except IOError:
                    png = Image.open(fullpath)
                    png.load()  # required for png.split()
                    background = Image.new("RGB", png.size, (255, 255, 255))
                    background.paste(png, mask=png.split()[3])
                    background.save(outfullpath, 'JPEG', quality=80)

                os.remove(fullpath)

            return JsonResponse({'true': 'ok','imgpath':outfullpath,'filenum':filenum,'shortcode':shortcode})

        elif mediatype == 'video':
            path = 'static/ins/videos_storage_temp/' + shortcode

            if not os.path.exists(path):
                os.mkdir(path)

            file = request.FILES['upfile']

            if not file:
                return JsonResponse({'false': 'upload fail'})

            tail = str(file).split('.').pop()
            outfullpath = os.path.join(path,'1.' + tail)



            with open(outfullpath, 'wb') as f:
                while True:
                    chunk = file.read(512)
                    if chunk:
                        f.write(chunk)
                    else:
                        break

            if tail != 'mp4':
                reverpath = os.path.join(path,'1.mp4')
                cmd = 'ffmpeg -i {} -strict -2 {}'.format(outfullpath,reverpath)
                pipe = subprocess.Popen(cmd, shell=True)
                pipe.wait()
                os.remove(outfullpath)
                outfullpath = reverpath # turn its back

            imgpath = 'static/ins/images_storage_temp/' + shortcode

            if not os.path.exists(imgpath):
                os.mkdir(imgpath)

            imgcrop_cmd = 'ffmpeg -ss 00:00:14 -i {} -frames:v 1 {}/1.jpg'.format(outfullpath, imgpath)
            imgpipe = subprocess.Popen(imgcrop_cmd, shell=True)
            imgpipe.wait()

            return JsonResponse({'true': 'ok', 'videopath': outfullpath, 'filenum': '1', 'shortcode': shortcode})


def up_avatar(request):
    username = request.COOKIES.get('islogin')
    file = request.FILES['avatar_file']
    path = 'static/ins/avatar/{}.jpg'.format(username)
    print path
    with open(path, 'wb') as f:
        while True:
            chunk = file.read(512)
            if chunk:
                f.write(chunk)
            else:
                break

    chscale((150,150),path,'jpg')

    return JsonResponse({'true':'change avatar success'})




def delete_temp(request, code, mediatype):
    if mediatype == 'image':
        shortcode,filenum = code.split(':')
        filepath = 'static/ins/images_storage_temp/{}/{}.jpg'.format(shortcode,filenum)
        try:
            os.remove(filepath)
        except:
            return JsonResponse({'false':'fail to delete'})
        return JsonResponse({'true':'succeed to delete'})
    elif mediatype == 'video':
        shortcode, filenum = code.split(':')
        filepath = 'static/ins/videos_storage_temp/{}/{}.mp4'.format(shortcode, filenum)
        imgfilepath = 'static/ins/images_storage_temp/{}/{}.jpg'.format(shortcode, filenum)
        try:
            os.remove(filepath)
            os.remove(imgfilepath)
        except:
            return JsonResponse({'false': 'fail to delete'})
        return JsonResponse({'true': 'succeed to delete'})


def savefile(request):
    mediatype = request.POST.get('mediatype')
    shortcode = request.POST.get('shortcode')
    username = request.COOKIES.get('islogin')
    user = InsUser.objects.get(username=username)

    article = InsArticle()

    time = str(datetime.now())[:-7]

    article.text = request.POST.get('text')
    article.pub_time = time
    article.shortcode = shortcode
    article.user = user

    crop_path = False
    crop_target_path = False
    if mediatype == 'image':
        article.type = 'image'
        dir_path = 'static/ins/images_storage_temp/' + shortcode
        target_path = 'static/ins/images_storage/' + shortcode

        shutil.copytree(dir_path, target_path)
    else:
        article.type = 'video'
        dir_path = 'static/ins/videos_storage_temp/' + shortcode
        target_path = 'static/ins/videos_storage/' + shortcode
        shutil.copytree(dir_path, target_path)

        crop_path = 'static/ins/images_storage_temp/' + shortcode
        crop_target_path = 'static/ins/images_storage/' + shortcode

        shutil.copytree(crop_path, crop_target_path)

    article.save()
    if dir_path and os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    if crop_path and os.path.exists(crop_path):
        shutil.rmtree(crop_path)
    log_info = 'username:{}, shortcode:{}'.format(username, shortcode)
    pub_logger.info(log_info)
    return JsonResponse({'true':'ok'})


def delete_article(request, shortcode):
    user = InsUser.objects.get(username=request.COOKIES.get('islogin'))
    article = InsArticle.objects.get(shortcode=shortcode)
    if article.user == user:
        if article.type == 'image':
            image_path = 'static/ins/images_storage/' + shortcode
            if os.path.exists(image_path):
                shutil.rmtree(image_path)
        else:
            image_path = 'static/ins/images_storage/' + shortcode
            video_path = 'static/ins/videos_storage/' + shortcode
            if os.path.exists(image_path):
                shutil.rmtree(image_path)
            if os.path.exists(video_path):
                shutil.rmtree(video_path)
        article.delete()
        return JsonResponse({'true': 'article has been deleted'})
    return JsonResponse({'false': 'article can,t be delete'})






def unload(request, shortcode, mediatype):
    crop_path = False

    if mediatype == 'image':
        path = 'static/ins/images_storage_temp/' + shortcode
    else:
        path = 'static/ins/videos_storage_temp/' + shortcode
        crop_path = 'static/ins/images_storage_temp/' + shortcode


    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            if crop_path:
                shutil.rmtree(crop_path)
        except Exception as e:
            return JsonResponse({'false':'cant do it'})
    return JsonResponse({'true':'ok'})


def gen_captcha():
    code_list = []
    for i in range(10):  # 0-9数字
        code_list.append(str(i))
    for i in range(65, 91):  # A-Z
        code_list.append(chr(i))
    for i in range(97, 123):  # a-z
        code_list.append(chr(i))

    random.shuffle(code_list)
    captcha = ''.join(code_list[:6])
    return captcha


def send_email(request, email):
    def send_email_inner():
        captcha = gen_captcha()
        my_sender = 'yinweiqiab@163.com'
        my_user = email
        server = smtplib.SMTP("smtp.163.com", 25)
        server.login(my_sender, "JohnSnow@321")
        html = '<html><body><div><h1>验证码</h1></div><div><h2>{}</h2></div></body></html>'.format(captcha)
        msg = MIMEText(html, 'html', 'utf-8')
        msg['From'] = formataddr(["ins", my_sender])
        msg['To'] = formataddr(["my friend", my_user])
        msg['subject'] = Header(u'ins验证码')
        try:
            server.sendmail(my_sender, my_user, msg.as_string())
        except smtplib.SMTPException:
            return JsonResponse({'false': '未知错误'})
        server.quit()

        request.session['captcha'] = captcha
        request.session['email_time'] = time.time()

        return JsonResponse({'true':'验证码已发送'})

    try:
        email_time = request.session['email_time']
        if time.time() - email_time > 60:
            response = send_email_inner()
            return response
        else:
            return JsonResponse({'false':'请等待60s'})
    except:
        response = send_email_inner()
        return response


def reset_pass_confirm(request):
    email = request.POST.get('email')
    captcha = request.POST.get('captcha')
    newpass = request.POST.get('newpass')
    confirm_newpass = request.POST.get('confirm_newpass')

    print request.session['captcha']
    if newpass != confirm_newpass:
        return JsonResponse({'false': '两次密码不一致'})
    if captcha != request.session['captcha']:
        return JsonResponse({'false': '验证码错误'})
    try:
        user = InsUser.objects.get(email=email)
        user.password = newpass
        user.save()
        return JsonResponse({'true': '更改密码成功'})
    except:
        return JsonResponse({'false': '未知错误'})







