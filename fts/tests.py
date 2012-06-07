# -*- coding: utf-8 -*-
from django_liveserver.testcases import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


class RegisterTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.browser = WebDriver()
        super(RegisterTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(RegisterTest, cls).tearDownClass()
        cls.browser.quit()


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
        first_name = self.browser.find_element_by_name('first_name')
        last_name = self.browser.find_element_by_name('last_name')
        username = self.browser.find_element_by_name('username')
        password1 = self.browser.find_element_by_name('password1')
        password2 = self.browser.find_element_by_name('password2')
        invite_code = self.browser.find_element_by_name('invite_code')
        first_name.send_keys('testuser')
        last_name.send_keys('usertester')
        username.send_keys('test@example.com')
        password1.send_keys('asdf1234')
        password2.send_keys('asdf1234')
        invite_code.send_keys('permanent1')

        # click the "Skapa konto" button
        button = self.browser.find_element_by_tag_name('button')
        button.click()
        WebDriverWait(self.browser, 10).until(
                lambda driver: driver.find_element_by_tag_name('body'))

        # make sure we logged in
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(u'Hej testuser', body.text)

        # make sure we arrived at signup-step1
        self.assertIn(u"Först, börja med att fylla i "
                      u"information om din salong", body.text)



class AboutStyleMatchTest(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.browser = WebDriver()
        super(AboutStyleMatchTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(AboutStyleMatchTest, cls).tearDownClass()
        cls.browser.quit()

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


