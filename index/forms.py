# coding:utf-8
from django import forms
from index.models import Tip
import re


class TipForm(forms.ModelForm):
    zip = forms.CharField(label="Postnummer",
                          max_length=5,
                          required=True,
                          widget=forms.TextInput(attrs={'class':'span1'}))

    def clean_zip(self):
        zip = self.cleaned_data.get('zip')
        m = re.search('^[0-9]{5}', zip)
        if m is None:
            raise forms.ValidationError(u"Ange ett giltigt postnummer.")
        return zip

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        phone = re.sub(r'\s', '', phone) # strip all whitespaces
        phone = re.sub(r'\+46','0', phone)

        # example valid phonenumbers:
        # 0761234567
        # 073-6456456
        # +4673-4567891
        # +45761234567
        m = re.search('^07[0-9]-?[0-9]{7}$', phone)
        if '-' not in phone:
            # 0731234567 --> 073-1234567
            phone = phone[:3] + u'-' + phone[3:]

        if m is None:
            raise forms.ValidationError(u'Ange ett giltigt telefonnummer.')

        query = Tip.objects.filter(phone=phone)
        if query:
            raise forms.ValidationError(u'Detta telefonnumret är redan anmält.')

        return phone

    class Meta:
        model = Tip
