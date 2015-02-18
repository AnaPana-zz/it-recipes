from django.test import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
import time

# class SeleniumTestLoginForm(LiveServerTestCase):
#     fixtures = ['user-data.json']
#     
#     @classmethod
#     def setUpClass(cls):
#         cls.selenium = WebDriver()
#         super(SeleniumTestLoginForm, cls).setUpClass()
# 
#     @classmethod
#     def tearDownClass(cls):
#         cls.selenium.quit()
#         super(SeleniumTestLoginForm, cls).tearDownClass()
# 
#     def test_valid_login(self):
#         self.selenium.get('%s%s' % ('http://192.168.247.129:8080', '/login'))
#         username_input = self.selenium.find_element_by_name("username")
#         username_input.send_keys('AnaPana')
#         password_input = self.selenium.find_element_by_name("password")
#         password_input.send_keys('MyNewItBlog')
#         self.selenium.find_element_by_xpath('//input[@value="Login"]').click()
#         time.sleep(2)
#         print '\ntest_valid_login'
#         self.assertTrue(self.selenium.find_element_by_xpath("//a[contains(text(), 'Blog')]"))
# 
#     def test_invalid_login_or_passwd(self):
#         self.selenium.get('%s%s' % ('http://192.168.247.129:8080', '/login'))
#         username_input = self.selenium.find_element_by_name("username")
#         username_input.send_keys('AnaPana')
#         password_input = self.selenium.find_element_by_name("password")
#         password_input.send_keys('MyNewItBlog1')
#         self.selenium.find_element_by_xpath('//input[@value="Login"]').click()
#         time.sleep(2)
#         print '\ntest_invalid_login'
#         self.assertTrue(self.selenium.find_element_by_xpath("//li[contains(text(), 'Please enter a correct username and password.')]"))

SITE_URL = '192.168.56.98:8080'

from django.utils import unittest
from main.models import Subject, Article
from django.contrib.auth.models import User

class ArticleTestCase(unittest.TestCase):
    def setUp(self):
        print "Testing Subject, User, Article"
        self.user = User.objects.create(username="TestUser",
                                        email="bla@mail.com",
                                        password="pwd")
        self.subj = Subject.objects.create(name="TestSubj")
        self.art = Article.objects.create(title="TestArticle",
                                          body="TestBody",
                                          subject=self.subj,
                                          author=self.user)

    def testArticle(self):
        self.assertEqual(self.art.title, "TestArticle")


from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

class SimpleTest(TestCase):

    def test_add_article(self):
        response = self.client.post(reverse('main.views.add_article'),
                                    {
                                     'title': 'Test article',
                                     'body': 'Test article body',
                                     'subject' : 2,
                                     'tags' : 'python,django'
                                    }, follow=True)
        print '\nTest adding article URL'
        self.assertEqual(response.status_code, 200)

    # Testing page responses
    def test_blog(self):
        response = self.client.get(reverse('main.views.blog', args=(0,)))
        print '\nTest blog URL'
        self.assertEqual(response.status_code, 200)

    def test_about(self):
        response = self.client.get(reverse('main.views.about'))
        print '\nTest about URL'
        self.assertEqual(response.status_code, 200)
 
    def test_tag_results(self):
        response = self.client.get(reverse('main.views.tag_results', args=('python',)))
        print '\nTest tag results URL'
        self.assertEqual(response.status_code, 200)

    def test_dashboard_articles(self):
        response = self.client.get(reverse('dashboard.views.articles'))
        print '\nTest dashboard articles'
        self.assertEqual(response.status_code, 302)
 
    def test_dashboard_drafts(self):
        response = self.client.get(reverse('dashboard.views.drafts'))
        print '\nTest dashboard drafts'
        self.assertEqual(response.status_code, 302)

    def test_dashboard_mycomments(self):
        response = self.client.get(reverse('dashboard.views.my_comments'))
        print '\nTest dashboard mycomments'
        self.assertEqual(response.status_code, 302)

    def test_dashboard_commentstome(self):
        response = self.client.get(reverse('dashboard.views.comments_to_me'))
        print '\nTest dashboard commentstome'
        self.assertEqual(response.status_code, 302)

    def test_dashboard_favorites(self):
        response = self.client.get(reverse('dashboard.views.favorites'))
        print '\nTest dashboard favorites'
        self.assertEqual(response.status_code, 302)
