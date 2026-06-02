from django import template

register = template.Library()


@register.filter
def price_class(price):
    try:
        p = float(price)
    except Exception:
        return ''
    if p >= 50000:
        return 'danger'
    if p >= 20000:
        return 'warn'
    if p > 0:
        return 'good'
    return ''


@register.filter
def risk_class(risk):
    try:
        r = float(risk)
    except Exception:
        return ''
    if r >= 70:
        return 'danger'
    if r >= 40:
        return 'warn'
    return 'good'
