#coding=utf-8
from email.mime.text import MIMEText
import smtplib
from email.utils import formataddr
from email.header import Header
from celery import task,platforms
my_sender = 'yinweiqiab@163.com'
import time

platforms.C_FORCE_ROOT =True





@task
def send_email_inner(email,captcha):
    my_user = email
    server = smtplib.SMTP_SSL("smtp.163.com", 465)
    server.login(my_sender, "ewqDSAcxz321")
    html = '<html><body><div><h1>验证码</h1></div><div><h2>{}</h2></div></body></html>'.format(captcha)
    msg = MIMEText(html, 'html', 'utf-8')
    msg['From'] = formataddr(["ins", my_sender])
    msg['To'] = formataddr(["my friend", my_user])
    msg['subject'] = Header(u'来自Ins的验证码')
    server.sendmail(my_sender, my_user, msg.as_string())
    server.quit()

