#translation filter used for wagtailmenus
from django import template

from wagtail.models import Site

register = template.Library()

@register.filter
def get_translation(page, language_code):
    try:
        return page.get_translation(language_code)
    except Exception:
        return None