#!/var/lib/openshift/54e6106d4382ec016200009b/python/virtenv/bin/python
import smtplib
import os
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


MAIL_ADDRESS='admin@it-recipes.com'
MAIL_PASSWORD='MyNewItRecipes'
MAIL_SERVER='smtp.mail.ru'
MAIL_PORT='2525'

def clean_spam_comments():
    django_path = os.path.join(os.environ.get('OPENSHIFT_REPO_DIR'), 'itblog')
    os.chdir(django_path)
    sys.path.append(django_path)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'itblog.settings'
    import django
    django.setup()
    from django.db.models import Q
    from main.models import Comment
    from tasks.models import Solution, SolutionComment
    qc = Q(body__icontains='Cheap Michael Kors')|Q(author__username__icontains='Cheap Michael Kors')|Q(name__icontains='Cheap Michael Kors')
    qs = Q(body__icontains='Cheap Michael Kors')|Q(author__username__icontains='Cheap Michael Kors')
    qsc = Q(body__icontains='Cheap Michael Kors')|Q(author__username__icontains='Cheap Michael Kors')|Q(author_name__contains='Cheap Michael Kors')
    comments = Comment.objects.filter(qc)
    solutions = Solution.objects.filter(qs)
    solutioncomments = SolutionComment.objects.filter(qsc) 
    email_body = """Comments: {0}
Solutions: {1}
SolutionComments: {2}
were deleted""".format(str([c.id for c in comments]), str([s.id for s in solutions]), str([sc.id for sc in solutioncomments])) 
    comments.delete()
    solutions.delete()
    solutioncomments.delete()
    _send_mail_to_admin('Remove spam comments', email_body)

def _send_mail_to_admin(subject, body):
    admin_mail = MAIL_ADDRESS
    receiver_mail = 'naka5@mail.ru'
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = admin_mail
    msg['To'] = receiver_mail
    message_body = MIMEText(body, 'plain')
    msg.attach(message_body)

    username = admin_mail
    password = MAIL_PASSWORD

    server = smtplib.SMTP('%s:%s' % (MAIL_SERVER, MAIL_PORT))
    server.starttls()
    server.login(username,password)
    server.sendmail(admin_mail, receiver_mail, msg.as_string())
    server.quit()

if __name__ == '__main__':
    clean_spam_comments()

