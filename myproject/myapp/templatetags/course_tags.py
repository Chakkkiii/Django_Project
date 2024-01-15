# app/templatetags/course_tags.py

from django import template

register = template.Library()

@register.filter
def discount_calculation(price, discount):
    try:
        price = float(price)
        discount = float(discount)
        discounted_price = price - (price * discount / 100)
        return "{:.2f}".format(discounted_price)
    except (ValueError, TypeError):
        return price  # Return the original price if there's an error
