import datetime

from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse


class StaticPagesSitemap(Sitemap):
    """Reverse static views for XML sitemap.
    http://stackoverflow.com/a/7072765
    """
    def items(self):
        # Return list of url names for views to include in sitemap
        return ['index_page', 'about_page', 'contact_page', 'inspiration_page', 'search']

    def location(self, item):
        return reverse(item)
