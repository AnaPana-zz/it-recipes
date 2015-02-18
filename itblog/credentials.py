import os

ADMIN_MAIL = {
              'address'  : os.environ.get('ADMIN_MAIL'),
              'password' : os.environ.get('ADMIN_PASS'),
              'server'   : os.environ.get('SMTP_SERVER'),
              'port'     : os.environ.get('SMTP_PORT'),
              }
