# -*- coding: utf-8 -*-
from django_liveserver.testcases import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


class RegisterTest(LiveServerTestCase):
    """
    Tests that a new user is able to register on the website
    """

    def setUp(self):
        self.browser = WebDriver()
        super(RegisterTest, self).setUp()

    def tearDown(self):
        super(RegisterTest, self).tearDown()
        self.browser.quit()

    def get_register_form(self):
        """returns a dict of all elements from the registration form"""
        return {
            'first_name': self.browser.find_element_by_name('first_name'),
            'last_name': self.browser.find_element_by_name('last_name'),
            'username': self.browser.find_element_by_name('username'),
            'password1': self.browser.find_element_by_name('password1'),
            'password2': self.browser.find_element_by_name('password2'),
            'invite_code': self.browser.find_element_by_name('invite_code'),
            'form': self.browser.find_element_by_tag_name('form'),
            'button': self.browser.find_element_by_name('register'),
        }

    def test_successful_register(self):
        # open browser and navigate to stylematch
        self.browser.get(self.live_server_url)

        # make sure it loaded
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(u"Hitta en kvalificerad frisör "
                      u"i ditt närområde och boka nu", body.text)

        # go to register page
        register = self.browser.find_element_by_link_text(
                                        u'Bli medlem som frisör')
        register.click()
        WebDriverWait(self.browser, 10).until(
                lambda driver: driver.find_element_by_tag_name('body'))

        # fill in the form
        form = self.get_register_form()
        form['first_name'].send_keys('testuser')
        form['last_name'].send_keys('usertester')
        form['username'].send_keys('test@example.com')
        form['password1'].send_keys('asdf1234')
        form['password2'].send_keys('asdf1234')
        form['invite_code'].send_keys('permanent1')

        # click the "Skapa konto" button
        form['button'].click()
        WebDriverWait(self.browser, 10).until(
                lambda driver: driver.find_element_by_tag_name('body'))

        # make sure we logged in
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(u'Hej testuser', body.text)

        # make sure we arrived at signup-step1
        self.assertIn(u"Först, börja med att fylla i "
                      u"information om din salong", body.text)

    def test_empty_register(self):
        self.browser.get(self.live_server_url + '/accounts/register/')

        # fill in and empty form
        form = self.get_register_form()
        form['form'].submit()
        errors = self.browser.find_elements_by_class_name('error')
        self.assertEqual(len(errors), 6)

    def test_missing_fields(self):
        self.browser.get(self.live_server_url + '/accounts/register/')

        form = self.get_register_form()
        form['first_name'].send_keys("firstname")
        form['form'].submit()
        errors = self.browser.find_elements_by_class_name('error')
        self.assertEqual(len(errors), 5)

        form = self.get_register_form()
        form['last_name'].send_keys("lastname")
        form['form'].submit()
        errors = self.browser.find_elements_by_class_name('error')
        self.assertEqual(len(errors), 4)

        form = self.get_register_form()
        form['username'].send_keys("test@example.com")
        form['form'].submit()
        errors = self.browser.find_elements_by_class_name('error')
        self.assertEqual(len(errors), 3)

        form = self.get_register_form()
        form['password1'].send_keys("passw123")
        form['form'].submit()
        errors = self.browser.find_elements_by_class_name('error')
        self.assertEqual(len(errors), 2)

        form = self.get_register_form()
        form['password1'].send_keys("passw123")
        form['password2'].send_keys("passw123")
        form['form'].submit()
        errors = self.browser.find_elements_by_class_name('error')
        self.assertEqual(len(errors), 1)


class AboutStyleMatchTest(LiveServerTestCase):

    def setUp(self):
        self.browser = WebDriver()
        super(AboutStyleMatchTest, self).setUp()

    def tearDown(self):
        super(AboutStyleMatchTest, self).tearDown()
        self.browser.quit()

    def test_reachable(self):
        # open browser and navigate to stylematch
        self.browser.get(self.live_server_url)

        # find the link "om stylematch" and click it
        about_link = self.browser.find_element_by_link_text("OM STYLEMATCH")
        about_link.click()
        # IMPORTANT: after 'click()' has been called, you must wait for the
        # page to load, otherwise NoSuchElementFound exception is likely
        # to happen
        WebDriverWait(self.browser, 10).until(
                lambda driver: driver.find_element_by_tag_name('body'))

        # find the text "Vilka är StyleMatch?"
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(u"Vilka är StyleMatch?", body.text)
