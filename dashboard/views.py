# coding:utf-8
import json
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from accounts.models import Service, OpenHours, GalleryImage, InviteCode
from django.views.generic import TemplateView
from braces.views import LoginRequiredMixin, StaffRequiredMixin
from dashboard.google_analytics import profile_statistics
from accounts.models import UserProfile

class DashboardView(LoginRequiredMixin, TemplateView):
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

        
        # Upload gallery image
        task = { 'url': reverse('edit_images'),
                 'text': u'Ladda upp din första galleribild',
                 'passed': True }
        try:
            GalleryImage.objects.get(user=userprofile.user)
        except GalleryImage.DoesNotExist:
            task['passed'] = False
        except GalleryImage.MultipleObjectsReturned:
            pass
        tasks_to_be_done.append(task)


        # Add open hours
        task = { 'url': reverse('profiles_add_hours'),
                 'text': u'Skriv in dina öppettider',
                 'passed': True }
        task['passed'] = userprofile.user.openhours.reviewed
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
        
        # if all tasks is done, return an empty list
        # so this won't be displayed in the template
        all_passed = len([0 for x in tasks_to_be_done if not x['passed']]) <= 0
        if all_passed:
            return []
        else:
            tasks_to_be_done = sorted(tasks_to_be_done, key=lambda k: k['passed'], reverse=True) 
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
        else:
            if ((not self.request.user.userprofile.visible) and
                    self.request.user.userprofile.approved):
                context['visibility_notification'] = {'approved': True }
            elif (self.request.user.userprofile.visible and
                  self.request.user.userprofile.approved):
                context['visibility_notification'] = {'visible': True }

        # visits statistics chart
        profile_url = self.request.user.userprofile.profile_url
        try:
            # since we use the list in a template, to create a javascript array
            # the python list needs to be converted to JSON
            context['visitor_count_data'] = json.dumps(profile_statistics.get_profile_visits(profile_url))
        # if the google api authentication key is missing
        except AttributeError:
            context['visitor_count_data'] = []

        return context


class InviteCodeView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    template_name = "invitecode.html"

    def get_context_data(self, **kwargs):
        context = super(InviteCodeView, self).get_context_data(**kwargs)

        # only hit the database once
        all_codes = InviteCode.objects.filter(inviter=self.request.user)
        unused_codes = all_codes.filter(reciever=None)
        used_codes = all_codes.exclude(reciever=None)

        context['codes'] = unused_codes
        context['used_codes'] = used_codes

        return context
