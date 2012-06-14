# -*- coding: utf-8 -*-
from django_liveserver.testcases import LiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select


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

    def test_successful_register_and_signup(self):
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

        # fill in the form
        salon_name = self.browser.find_element_by_name('salon_name')
        salon_adress = self.browser.find_element_by_name('salon_adress')
        salon_city = self.browser.find_element_by_name('salon_city')
        priv_phone = self.browser.find_element_by_name(
                                    'personal_phone_number')
        work_phone = self.browser.find_element_by_name('salon_phone_number')
        displayed_phone = Select(self.browser.find_element_by_name(
                                            'number_on_profile'))
        salon_name.send_keys("TestSalong")
        salon_adress.send_keys("Test street 27A")
        salon_city.send_keys("TestyTown")
        priv_phone.send_keys("+4673-0123456")
        work_phone.send_keys("0123-12345")
        displayed_phone.select_by_visible_text('Personligt telefonnummer')

        # continue to next step by clicking button
        button = self.browser.find_element_by_xpath(
                                    u"//button[contains(text(), 'Spara och gå vidare')]")
        button.click()
        WebDriverWait(self.browser, 10).until(
                lambda driver: driver.find_element_by_tag_name('body'))

        # make sure we arrived at signup-step2
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(u'öppettider', body.text)

        # form is already filled in, just count the number of selects so
        # nothing went wrong
        selects = self.browser.find_elements_by_tag_name('select')
        self.assertEquals(len(selects), 14)

        # continue to next step by clicking button
        button = self.browser.find_element_by_css_selector(
                                    u"input[value='Spara och gå vidare']")
        button.click()
        WebDriverWait(self.browser, 10).until(
                lambda driver: driver.find_element_by_tag_name('body'))

        # make sure we arrived at signup-step3
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(u'prislista', body.text)

        # add a new treatment
        name = self.browser.find_element_by_name('name')
        desc = self.browser.find_element_by_name('description')
        time = Select(self.browser.find_element_by_name('length'))
        price = self.browser.find_element_by_name('price')
        add = self.browser.find_element_by_xpath(
                                    u"//button[contains(text(), 'Lägg till')]")
        name.send_keys(u'Klippning')
        desc.send_keys(u'Inklusive styling')
        time.select_by_visible_text('1 timme')
        price.send_keys('45')
        add.click()

        # wait for the new treatment to appear in the list
        # NOTE: div[@class] must match a FULL STRING, not individual
        # classes
        WebDriverWait(self.browser, 10).until(
                lambda driver: driver.find_element_by_xpath(
                       u"//div[@class='service-name unique-list-item-part']"
                        "/b[contains(text(), 'Klippning')]"))

        cont = self.browser.find_element_by_link_text(u'Spara och gå vidare')
        cont.click()
        WebDriverWait(self.browser, 10).until(
                lambda driver: driver.find_element_by_tag_name('body'))

        # make sure we arrived at signup-step4
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn(u'Sista steget', body.text)
        # NOTE:
        # We should test actual upload of an image but that is currently not
        # possible in selenium if we use an <input type='file'> field.
        # Skip this test for now
        #
        # doupload = self.browser.find_element_by_link_text('Ladda upp profilbild')
        # doupload.click()
        skipupload = self.browser.find_element_by_link_text(u"Gå vidare utan "
                                            "att ladda upp profilbild")
        skipupload.click()
        WebDriverWait(self.browser, 10).until(
                lambda driver: driver.find_element_by_tag_name('body'))

        # make sure we arrived at the profile
        # 'testuser' comes from firstname
        toplink = self.browser.find_element_by_link_text(u'Hej testuser')

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

    def test_register_taken_email(self):
        """
        TODO: What happens when someone tries to register with an email that
        already exists?
        """
        pass
