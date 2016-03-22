from django import template
from datetime import datetime

register = template.Library()

@register.filter
def convertXValueToString(value):
    if isinstance(value, datetime):
        return datetime.strftime(value, "%d %b %Y")
    return value