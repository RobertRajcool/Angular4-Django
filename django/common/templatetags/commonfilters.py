from django import template
register = template.Library()
@register.filter
def return_item(l, i):
    try:
        return l[i]
    except:
        return None
@register.filter
def currency(value, currecny_format):
    import locale
    try:
        if currecny_format == 1:
            locale.setlocale(locale.LC_ALL, 'en_IN')
        else:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        locale.setlocale(locale.LC_ALL, '')
    loc = locale.localeconv()
    return locale.currency(float(value), loc['currency_symbol'], grouping=True)
@register.simple_tag
def constant_value(name):
    from cloudapp.generics.constant import AppContants
    ALLOWABLE_VALUES = ("DOMAIN_NAME")
    if name in ALLOWABLE_VALUES:
        return getattr(AppContants, name, '')
    return ''