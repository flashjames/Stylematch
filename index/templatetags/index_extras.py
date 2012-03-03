"""
Global filters needed in all templates
"""

from django import template
register = template.Library()

# Now, inside a template you can do {{ template_var|pdb }} and enter a pdb session
@register.filter 
def pdb(element):
    import ipdb; ipdb.set_trace()
    return element


