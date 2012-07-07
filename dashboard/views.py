# coding:utf-8
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from accounts.models import Service, OpenHours, GalleryImage

class DashboardView(TemplateView):
    template_name="dashboard.html"

    def get_tasks_to_be_done(self, userprofile):
        # get tasks to be done as a list of tasks
        # 'tasks_to_be_done' : [{ 'url': url,
        #                         'text': 'msg',
        #                         'passed': Done? },]
        tasks_to_be_done = []

        # Create an account (automatically done)
        task = { 'url': reverse('profile_display_with_profile_url',
                            kwargs={'slug': userprofile.profile_url}),
                 'text': u'Gör ditt StyleMatch-konto',
                 'passed': True }
        tasks_to_be_done.append(task)

        # Information about salon. Address, phone etc
        task = { 'url': reverse('profile_edit'),
                 'text': u'Fyll i salongsinformation',
                 'passed': False }
        if (userprofile.salon_name and
                userprofile.salon_city and
                userprofile.salon_adress and
                userprofile.zip_adress and
                userprofile.salon_phone_number):
            task['passed'] = True
        tasks_to_be_done.append(task)

        # Upload profile image
        task = { 'url': reverse('edit_images'),
                 'text': u'Ladda upp en profilbild',
                 'passed': False }
        if (userprofile.profile_image_cropped or
                userprofile.profile_image_uncropped):
            task['passed'] = True
        tasks_to_be_done.append(task)

        # Add open hours
        task = { 'url': reverse('profiles_add_hours'),
                 'text': u'Skriv in dina öppettider',
                 'passed': True }
        try:
            oh = OpenHours.objects.get(user=userprofile.user)
            task['passed'] = oh.reviewed
        except OpenHours.DoesNotExist:
            task['passed'] = False
        tasks_to_be_done.append(task)

        # Add services
        task = { 'url': reverse('profiles_edit_services'),
                 'text': u'Lägg upp din prislista',
                 'passed': True }
        try:
            s = Service.objects.get(user=userprofile.user)
        except Service.DoesNotExist:
            task['passed'] = False
        except Service.MultipleObjectsReturned:
            pass
        tasks_to_be_done.append(task)

        # Description about the stylist
        task = { 'url': reverse('profile_edit'),
                 'text': u'Skriv din personliga information',
                 'passed': False }
        if userprofile.profile_text:
            task['passed'] = True
        tasks_to_be_done.append(task)

        # Upload gallery image
        task = { 'url': reverse('edit_images'),
                 'text': u'Ladda upp din första galleribild!',
                 'passed': True }
        try:
            GalleryImage.objects.get(user=userprofile.user)
        except GalleryImage.DoesNotExist:
            task['passed'] = False
        except GalleryImage.MultipleObjectsReturned:
            pass
        tasks_to_be_done.append(task)


        # if all tasks is done, return an empty list
        # so this won't be displayed in the template
        all_passed = len([0 for x in tasks_to_be_done if not x['passed']]) <= 0
        if all_passed:
            return []
        return tasks_to_be_done

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        context['tasks_to_be_done'] = self.get_tasks_to_be_done(
                            self.request.user.userprofile)
        if context['tasks_to_be_done']:
            context['actual_tasks_to_do'] = len(
                    [0 for x
                     in context['tasks_to_be_done']
                     if not x['passed']])

        return context
