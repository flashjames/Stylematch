# -*- coding: utf-8 -*-
from django_liveserver.testcases import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait


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
