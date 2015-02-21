Deploying blog on [OpenShift](https://www.openshift.com/ "OpenShift")
===========================

1. Create Python2.7 application on openshift.
2. Add MySQL5.5 cartridge. Write down the db name.
3. Create ssh key on your local machine and add public key to your openshift app.
4. Fork this repo and clone to your local machine.
5. Add openshift as second remote repo:<br>
```git remote add openshift ssh://ydfg8sdf6g8o7sbrtsogpdfgs@<my_app>.rhcloud.com/~/git/blog.git/```<br>
6. Open file ```itblog/itblog/settings.py``` and change db name on yours (from #2).
7. Open file ```itblog/credentials.py``` and past there your mail settings (I can't still add env vars on openshift - TODO).
8. There are two action hooks:
 * ```.openshift/action_hooks/pre_start```
 * ```.openshift/action_hooks/post_start_mysql-5.5```<br>
The second one creates missing table and superuser. Remember superuser credentials and **remove** this hook after first launch. You'll need to change superuser credentials in blog's dashboard.
9. Push your code to openshift:
```git push openshift master --force```


For local development
=====================

1. Add the following environment variables to ~/.profile and source it.<br>
```ADMIN_MAIL='admin@gmail.com' && export ADMIN_MAIL
ADMIN_PASS='pass' && export ADMIN_PASS
SMTP_SERVER='smtp.gmail.com' && export SMTP_SERVER
SMTP_PORT='2525' && export SMTP_PORT
ITBLOG_APP_HOST='192.168.56.110' && export ITBLOG_APP_HOST
ITBLOG_APP_PORT='8080' && export ITBLOG_APP_PORT```

2. Create python virtual environment (http://docs.python-guide.org/en/latest/dev/virtualenvs) and install requirements:<br>
```pip install -r requirements.txt```

