from django.test import TestCase, LiveServerTestCase, Client
from django.contrib.auth.models import User
from django.db.models import Q

from mock import patch, Mock
from selenium.webdriver.firefox.webdriver import WebDriver

from .views import get_comment_dialog, get_comments_tree, get_recent_articles
from .models import Subject, UsefulLink, Article
from .forms import UsefulLinkForm, SubjectForm
from .utils import get_neighbors, send_mail, get_pagination_info, get_query, normalize_query

import smtplib

class TestStaticResponses(TestCase):

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


class TestSubjects(TestCase):
    """Class for testing base "subject" page elements,
    subject's actions in view and subject's form.
    """
    
    def test_subjects_url(self):
        response = self.client.get('/subject', follow=True)
        self.assertEqual(response.redirect_chain,
                         [('http://testserver/accounts/login/?next=/subject', 302)])
    
    def test_form_valid_data(self):
        form = SubjectForm({
            'name': 'my subject',
            'parent_subject': None,
        })
        self.assertTrue(form.is_valid())
        subject = form.save()
        self.assertEqual(subject.name, 'my subject')
        self.assertEqual(subject.parent_subject, None)
        
        form = SubjectForm({
            'name': 'child subject',
            'parent_subject': subject.id,
        })
        self.assertTrue(form.is_valid())
        child_subject = form.save()
        self.assertEqual(child_subject.name, 'child subject')
        self.assertEqual(child_subject.parent_subject, subject)

    def test_blank_data(self):
        form = SubjectForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': [u'This field is required.'],
        })
    
    def test_subject_actions(self):
        self.user = User.objects.create_superuser('bbb', 'aaa@mail.ru', '123')
        self.client.post('/login', {'username': self.user.username,
                                    'password' : '123'})
        self.client.post('/subject', {'name' : 'yours subject'})
        subject = Subject.objects.get(name='yours subject')
        self.assertEqual(subject.name, 'yours subject')
        
        response = self.client.post('/subject', {'edit_request' : True,
                                                 'item_id' : subject.id})
        self.assertTemplateUsed(response, 'main/forms/rowform.html')
        
        self.client.post('/subject', {'edit_submit' : True,
                                      'item_id' : subject.id,
                                      'name' : 'my new subject'})
        subject = Subject.objects.get(id=subject.id)
        self.assertEqual(subject.name, 'my new subject')
        
        response = self.client.post('/subject', {'delete_request' : True,
                                                 'item_id' : subject.id})
        with self.assertRaises(Subject.DoesNotExist) as e:
            Subject.objects.get(id=subject.id)
        

class TestBlogUserLoggedIn(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_superuser('bbb', 'aaa@mail.ru', '123')
        self.subject = Subject.objects.create(name='python')
        self.article = Article.objects.create(title='My First Article', body='Body',
                                         author=self.user, subject=self.subject, is_published=True)
        self.client.post('/login', {'username': self.user.username,
                                               'password' : '123'})

    def add_article_to_favourite(self):
        response = self.client.get('/articles/blog/%s' % self.article.id,
                                   {'add_request' : True, 'type' : 'favourite'})
        f, created = Favourite.objects.get_or_create(article=self.article,
                                                     owner=self.user)
        self.assertEqual(created, True)
        self.assertEqual(response.status_code, 200)
        
    def tearDown(self):
        self.article.delete()
        self.user.delete()
        self.subject.delete()
        self.client.get('/logout')


class TestBlogUserIsNotLoggedIn(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_superuser('bbb', 'aaa@mail.ru', '123')
        self.subject = Subject.objects.create(name='python')
        self.article = Article.objects.create(title='My First Article', body='Body',
                                         author=self.user, subject=self.subject, is_published=True)
    
    def test_home_url(self):
        response = self.client.get('/', follow = True)
        self.assertEqual(response.redirect_chain, 
                         [('http://testserver/articles/recent/0', 301)],)
 
    def test_blog_template(self):
        response = self.client.get('/articles/blog/%s' % self.article.id)
        self.assertTemplateUsed(response, 'main/blog/blog.html')
        self.assertTemplateUsed(response, 'main/blog/article.html')
 
    def test_unexisted_article_url(self):
        response = self.client.get('/articles/blog/999999', follow = True)
        self.assertEqual(response.redirect_chain, 
                         [('http://testserver/articles/recent/0', 302)],)

    def test_existed_article(self):
        response = self.client.get('/articles/blog/%s' % self.article.id)
        self.assertNotContains(response, 'Add to favorites')
        self.assertNotContains(response, '<a href="/article/edit/%s" class="btn btn-info">Edit article</a>' % self.article.id)
        self.assertNotContains(response, '<a href="#" class="btn btn-danger" onclick="remove_article(event, \'%s\')">Delete article</a>' % self.article.id)
        self.assertContains(response, 'My First Article')
        self.assertEqual(response.status_code, 200)
    
    def test_refresh_captcha(self):
        response = self.client.get('/articles/blog/%s' % self.article.id,
                                   {'refresh_captcha' : True},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.article.delete()
        self.user.delete()
        self.subject.delete()


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
    
    def tearDown(self):
        self.client.get('/logout')


class TestUtils(TestCase):
    """Class for testing main/utils.py module
    """
    
    def test_get_neighbors(self):
        self.assertEqual((1, 3), get_neighbors(2, [1,2,3]))
        self.assertEqual((None, 2), get_neighbors(1, [1,2,3]))
        self.assertEqual((2, None), get_neighbors(3, [1,2,3]))
    
    def test_send_mail(self):
        with patch("smtplib.SMTP") as mock_smtp:
            send_mail('bla@boo.com', 'this is subject', 'this is body')
        from credentials import ADMIN_MAIL
        mock_smtp.assert_called_once_with('%s:%s' % (ADMIN_MAIL['server'],
                                                     ADMIN_MAIL['port']))
    
    def test_get_pagination_info(self):
        self.assertEqual({'range_step' : 10,
                          'page_range' : [1, 2],
                          'p' : 1,
                          'delta' : 10,
                          'delta_range' : [10, 20, 30],
                          'lst_len' : 20,
                          'all' : False,
                         },
                         get_pagination_info(20, 1, 10))
        self.assertEqual({'range_step' : 10,
                          'page_range' : [1],
                          'p' : 1,
                          'delta' : 10,
                          'delta_range' : [10, 20, 30],
                          'lst_len' : 10,
                          'all' : True,
                         },
                         get_pagination_info(10, 1, 10))
        self.assertEqual({'range_step' : 10,
                          'page_range' : [1,2,3,4,5,6],
                          'p' : 4,
                          'delta' : 10,
                          'delta_range' : [10, 20, 30],
                          'lst_len' : 55,
                          'all' : False,
                         },
                         get_pagination_info(55, 4, 10))
    
    @patch('main.utils.normalize_query')
    def test_get_query(self, mock_normalize_query):
        mock_normalize_query.return_value=['some', 'words', 'with quotes']
        result = get_query('  some  words "with   quotes  "', ('title', 'body'))
        expected = (Q(**{'title__icontains' : 'some'}) | Q(**{'body__icontains' : 'some'})) & \
                   (Q(**{'title__icontains' : 'words'}) | Q(**{'body__icontains' : 'words'})) & \
                   (Q(**{'title__icontains' : 'with quotes'}) | Q(**{'body__icontains' : 'with quotes'}))
        for i, j in zip(result.__dict__['children'], expected.__dict__['children']):
            self.assertEqual(i.__dict__, j.__dict__)
    
    def test_normalize_query(self):
        self.assertEqual(normalize_query('  some random  words "with   quotes  " and   spaces'),
                         ['some', 'random', 'words', 'with quotes', 'and', 'spaces'])
        
        

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