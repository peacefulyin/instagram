#coding=utf-8
from django.conf.urls import url
from ins import views
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^$',RedirectView.as_view(url='/index')),
    url(r'index/$',views.index),
    url(r'qweasd/(.*)$',views.qweasd),
    url(r'blog/(.*)$',views.blog),
    url(r'login$',views.login),
    url(r'home$',views.home),
    url(r'article/delete/(.*)$',views.delete_article),
    url(r'explore_more/(.*)$',views.explore_more),
    url(r'explore/recently$',views.recently),
    url(r'explore/search/(.*)$',views.explore_search),
    url(r'explore/(.*?)/(.*)$',views.blog_more),
    url(r'account/edit$',views.edit),
    url(r'account/chpass$',views.chpass),
    url(r'account/chpass/backend$',views.chpass_backend),
    url(r'account/friend/addsign$',views.addsign),
    url(r'account/manage_access$',views.manage_access),
    url(r'account/comment_filter$',views.comment_filter),
    url(r'account/email_set$',views.email_set),
    url(r'account/contact_history$',views.contact_history),
    url(r'account/resetpass$',views.reset_pass),
    url(r'account/resetpass/veri_email/(.*)$',views.veri_email),
    url(r'account/resetpass/sendmail/(.*)$',views.send_email),
    url(r'account/resetpass/confirm$',views.reset_pass_confirm),
    url(r'account/friend/signfriend/(.*)', views.signfriend),
    url(r'explore/people$',views.explore_people),
    url(r'explore$',views.explore),
    url(r'account/signin$',views.signin),
    url(r'account/signup$',views.signup),
    url(r'account/release$',views.release),
    url(r'article/detail/(.*?)/(.*)', views.show_detail),
    url(r'article/leave_comment', views.leave_comment),
    url(r'give_me_content/(.*)',views.sendContent),
    url(r'inext_comment/(.*?)/(.*)', views.index_sendComment),
    url(r'next_comment/(.*?)/(.*)', views.sendComment),
    url(r'account/add_like/(.*)', views.add_like),
    url(r'account/remove_like/(.*)', views.remove_like),
    url(r'account/add_follow/(.*)', views.add_follow),
    url(r'account/remove_follow/(.*)', views.remove_follow),
    url(r'comment/delete/(.*)', views.delete_comment),
    url(r'upfile$', views.upfile),
    url(r'upfile/avatar$', views.up_avatar),
    url(r'delete_temp/(.*?)/(.*)', views.delete_temp),
    url(r'commit_upload', views.savefile),
    url(r'unload/(.*?)/(.*)', views.unload),






]

