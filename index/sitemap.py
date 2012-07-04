#-*- coding:utf-8 -*-
from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class StaticPagesSitemap(Sitemap):
    """Reverse static views for XML sitemap.
    http://stackoverflow.com/a/7072765
    """
    def items(self):
        # Return list of url names for views to include in sitemap

        # should remove linkoping, when we've added all cities
        return ['index_page', 'about_page', 'contact_page',
                'inspiration_page', 'search', 'linkoping']

    def location(self, item):
        # ugly hack to add linkoping to sitemap
        if item == "linkoping":
            return u"/linköping/"

        return reverse(item)
