# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models




class InsUser(models.Model):
    full_name = models.CharField(max_length=30)
    username = models.CharField(unique=True, max_length=30)
    password = models.CharField(max_length=30)
    phone = models.IntegerField(blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True,unique=True)
    about_self = models.CharField(max_length=1000, blank=True, null=True)
    gender = models.IntegerField(default=3)
    is_private = models.IntegerField(default=False)
    is_verified = models.IntegerField(default=False)

    class Meta:
        managed = False
        db_table = 'ins_user'


class InsArticle(models.Model):
    text = models.TextField(blank=True, null=True)
    pub_time = models.DateTimeField()
    user = models.ForeignKey(InsUser)
    shortcode = models.CharField(max_length=100,unique=True)
    type = models.CharField(max_length=20, blank=True, null=True)
    file_total = models.IntegerField(blank=True, null=True,default=1)

    class Meta:
        managed = False
        db_table = 'ins_article'


class InsBlock(models.Model):
    people = models.ForeignKey(InsUser, related_name='block_people')
    target = models.ForeignKey(InsUser, related_name='block_target')

    class Meta:
        managed = False
        db_table = 'ins_block'

class InsSign(models.Model):
    people = models.ForeignKey(InsUser, related_name='sign_people')
    article = models.ForeignKey(InsArticle, related_name='sign_article')
    target = models.ForeignKey(InsUser, related_name='sign_target')
    pub_time = models.DateTimeField(null=True)
    has_read = models.BooleanField(default=False)

    class Meta:
        db_table = 'ins_sign'

class InsLike(models.Model):
    user = models.ForeignKey(InsUser)
    article = models.ForeignKey(InsArticle)
    class Meta:
        managed = False
        db_table = 'ins_like'


class InsComment(models.Model):
    content = models.CharField(max_length=1000, blank=True, null=True)
    pub_time = models.DateTimeField()
    article = models.ForeignKey(InsArticle)
    user = models.ForeignKey(InsUser)

    class Meta:
        managed = False
        db_table = 'ins_comment'


class InsFriend(models.Model):
    people = models.ForeignKey(InsUser, related_name='firend_people')
    target = models.ForeignKey(InsUser, related_name='firend_target')

    class Meta:
        managed = False
        db_table = 'ins_friend'






