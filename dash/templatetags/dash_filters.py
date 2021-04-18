from django import template

register = template.Library()

@register.filter(name='divide')
def divide(value, arg):
	try:
		if int(arg)!=0: 
			return round(((float(value) / float(arg))* 100))
		else: 
			return 0

	except (ValueError, ZeroDivisionError):
		return None

@register.filter(name='substract')
def substract(value, arg):
	try:
		if int(arg)!=0: 
			return round(float(value) - float(arg))
		else: 
			return 0

	except (ValueError, ZeroDivisionError):
		return None

@register.filter(name='add')
def substract(value, *args):
	try:
		if int(arg)!=0: 
			sum = float(value)
			for elem in args : 
				sum += float(elem)
			return round(sum)
		else: 
			return 0

	except (ValueError, ZeroDivisionError):
		return None

@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, basestring):
        return text.startswith(starts)
    return False