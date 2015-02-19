from django.test import TestCase, LiveServerTestCase, Client
from django.contrib.auth.models import User

from mock import MagicMock, patch
from selenium.webdriver.firefox.webdriver import WebDriver

from .views import get_comment_dialog, get_comments_tree, get_recent_articles
from .models import Subject, UsefulLink, Article
from .forms import UsefulLinkForm


class TestResponses(TestCase):

    def test_home_url(self):
        response = self.client.get('/', follow = True)
        self.assertEqual(response.redirect_chain, 
                         [('http://testserver/articles/recent/0', 301)],)
 
    def test_unexisted_article_url(self):
        response = self.client.get('/articles/blog/999999', follow = True)
        self.assertEqual(response.redirect_chain, 
                         [('http://testserver/articles/recent/0', 302)],)

#     def test_existed_article_url(self):
#         user = User.objects.create_superuser('bbb', 'aaa@mail.ru', '123')
#         subject = Subject.objects.create(name='python')
#         article = Article.objects.create(title='My First Article', body='Body',
#                                          author=user, subject=subject)
#         response = self.client.get('/articles/blog/1')
#         self.assertContains(response, 'My First Article')
#         self.assertEqual(response.status_code, 200)

    def test_subjects_url(self):
        response = self.client.get('/links')
        self.assertEqual(response.status_code, 200)

    def test_links_url(self):
        response = self.client.get('/links')
        self.assertEqual(response.status_code, 200)

    def test_about_url(self):
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_logout_url(self):
        response = self.client.get('/logout', follow=True)
        self.assertEqual(response.redirect_chain, 
                         [('http://testserver/', 302),
                          ('http://testserver/articles/recent/0', 301)
                          ])


class TestStaticFunctions(TestCase):

    @patch('main.models.Comment.objects')
    def test_get_comment_dialog(self, c_objects):
        comment_id = 2
        c_objects.get.return_value = {'id' : comment_id}
        c_objects.filter.return_value = {}
        result = get_comment_dialog(comment_id)
        self.assertEqual(result,
                         {'parent_comment' : {'id' : comment_id},
                          'children' : []})

    @patch('main.models.Comment.objects.filter')
    def test_get_comments_tree(self, c_objects):
        c = c_objects.return_value
        c.order_by.return_value = [1,2,3]
        result = get_comments_tree(2)
        self.assertEqual(result,
                         [{'parent_comment' : 1, 'children' : c},
                          {'parent_comment' : 2, 'children' : c},
                          {'parent_comment' : 3, 'children' : c}])

    @patch('main.models.Article.objects.filter')
    def test_get_recent_articles(self, a_objects):
        a = a_objects.return_value
        a.order_by.return_value = [1,2,3,4,5]
        result = get_recent_articles()
        self.assertEqual(result, [1,2,3])


class TestUsefulLinks(TestCase):
    
    def setUp(self):
        self.subject = Subject.objects.create(name='python')

    def test_add_link_with_model(self):
        link = UsefulLink.objects.create(subject=self.subject,
                                         url='http://localhost',
                                         description='my link'
                                         )
        response = self.client.get('/links')
        self.assertContains(response, 'my link')
    
    def test_add_link_with_post(self):
        response = self.client.post('/links', {'subject': self.subject,
                                               'url': 'http://localhost',
                                               'description' : 'my link'})
        self.assertEqual(response.status_code, 200)

    def test_delete_link_with_post(self):
        link = UsefulLink.objects.create(subject=self.subject,
                                         url='http://localhost',
                                         description='my link'
                                         )
        self.client.post('/links', {'delete_request': 1,
                                    'item_id': link.id})
        response = self.client.get('/links')
        self.assertNotContains(response, 'my link')
        self.assertEqual(response.status_code, 200)

    def test_valid_data(self):
        form = UsefulLinkForm({
            'url': 'http://localhost',
            'subject': self.subject.id,
            'description': 'my link',
        })
        self.assertTrue(form.is_valid())
        link = form.save()
        self.assertEqual(link.url, 'http://localhost/')
        self.assertEqual(link.subject, self.subject)
        self.assertEqual(link.description, 'my link')
    
    def test_blank_data(self):
        form = UsefulLinkForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'url': [u'This field is required.'],
            'subject': [u'This field is required.'],
        })
        
    def test_errors_on_page(self):
        user = User.objects.create_superuser('aaa', 'aaa@mail.ru', '123')
        response = self.client.post('/login', {'username': 'aaa',
                                               'password' : '123'})
        response = self.client.post('/links', {})
        self.assertContains(response, 'This field is required.')

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
# 
# SITE_URL = '192.168.56.98:8080'
# 
# from django.utils import unittest
# from main.models import Subject, Article
# from django.contrib.auth.models import User
# 
# class ArticleTestCase(unittest.TestCase):
#     def setUp(self):
#         print "Testing Subject, User, Article"
#         self.user = User.objects.create(username="TestUser",
#                                         email="bla@mail.com",
#                                         password="pwd")
#         self.subj = Subject.objects.create(name="TestSubj")
#         self.art = Article.objects.create(title="TestArticle",
#                                           body="TestBody",
#                                           subject=self.subj,
#                                           author=self.user)
# 
#     def testArticle(self):
#         self.assertEqual(self.art.title, "TestArticle")