import re
import json
import smtplib
import os

from credentials import ADMIN_MAIL

from django.db.models import Q
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.http import HttpResponse
from django.contrib.auth.models import User


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    """ These functions were taken from great post:
        http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
        
        Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    """
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    """ Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    """
    query = None # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def get_pagination_info(lst_len, p=1, delta=10):
    range_step = 10 # range for "select" elemnt on the page for show results per page
    delta_range = range(range_step, range_step*4, range_step)
    
    if delta and lst_len:
        page_range = range(1, lst_len // delta + (lst_len % delta and 2 or 1))
    else:
        page_range = range(1, 2)
    
    pagination = {'range_step' : range_step,
                  'page_range' : page_range,
                  'p' : p,
                  'delta' : delta,
                  'delta_range' : delta_range,
                  'lst_len' : lst_len,
                  'all' : delta == lst_len,
                }
    
    return pagination


def send_mail(recipients_list, subject, body):
    super_emails = ";".join(set([u.email for u in User.objects.all() if u.is_superuser]))
    recipients = ";".join(recipients_list) + ";" + super_emails
    
    admin_mail = ADMIN_MAIL['address']
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = admin_mail
    msg['To'] = recipients_list
    message_body = MIMEText(body, 'plain')
    msg.attach(message_body)
    
    username = admin_mail
    password = ADMIN_MAIL['password']

    server = smtplib.SMTP('%s:%s' % (ADMIN_MAIL['server'],
                                     ADMIN_MAIL['port']))
    server.starttls()  
    server.login(username,password)
    server.sendmail(admin_mail, recipients_list, msg.as_string())
    server.quit()


def refresh_captcha():
    to_json_responce = dict()
    to_json_responce['new_cptch_key'] = CaptchaStore.generate_key()
    to_json_responce['new_cptch_image'] = captcha_image_url(to_json_responce['new_cptch_key'])

    return HttpResponse(json.dumps(to_json_responce), content_type='application/json')


def get_neighbors(item, list):
    """
    Returns previous and next items in list
    """
    
    i = list.index(item)
    previous = list[i-1] if list and i-1 >= 0 else None
    next = list[i+1] if list and i+1 < len(list) else None
        
    return previous, next