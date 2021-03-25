from django import template

from panel.handlers import is_demo as check_is_demo

register = template.Library()


@register.simple_tag()
def is_demo() -> bool:
    if check_is_demo():
        return True

    return False
