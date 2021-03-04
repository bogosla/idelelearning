from django import template 
from django.utils.safestring import mark_safe
import markdown 
register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))

@register.filter 
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return none
