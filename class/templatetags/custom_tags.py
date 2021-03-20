from django import template

register = template.Library()

def get_list_item(value, arg):
    return value[arg]


register.filter('get_list_item', get_list_item)