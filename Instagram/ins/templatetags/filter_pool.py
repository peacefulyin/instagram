import os
from django import template

from ins.models import *

register = template.Library()
static_path = '/var/www/ins/'


@register.filter
def like_veri(article, username):
    try:
        user = InsUser.objects.get(username=username)
        object_like = InsLike.objects.get(user=user, article=article)
        if object_like:
            return 'true'
        else:
            return 'false'
    except:
        return 'false'

@register.filter
def follow_veri(target_full_name, username):
    try:
        people = InsUser.objects.get(username=username)
        target = InsUser.objects.get(full_name=target_full_name)
        object_friend = InsFriend.objects.get(people=people, target=target)
        if object_friend:
            return 'true'
        else:
            return 'false'
    except:
        return 'false'


@register.filter
def self_veri(target_full_name, username):
    try:
        people = InsUser.objects.get(username=username)
        target = InsUser.objects.get(full_name=target_full_name)
        object_friend = InsFriend.objects.get(people=people, target=target)
        if object_friend:
            return 'true'
        else:
            return 'false'
    except:
        return 'false'

@register.filter
def vari_veri(shortcode):
    path = static_path + 'static/ins/images_storage/' + shortcode
    img_total = len(os.listdir(path))
    if img_total > 1:
        return 'true'
    return 'false'
