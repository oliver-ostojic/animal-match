from django import template

from matcher.models import Quiz

register = template.Library()


@register.filter(name='articulate')
def articulate(value):
    if value[0].lower() in 'aeiou':
        return f'an'
    else:
        return f'a'


@register.filter(name='all_lower')
def all_lower(value):
    return value.lower()


@register.filter(name='format_locations')
def format_locations(locations):
    if not locations:
        return ''
    if len(locations) == 1:
        return locations[0]
    return ', '.join(locations[:-1]) + ' or ' + locations[-1]


@register.filter(name='get_rank')
def get_rank(quiz):
    quizzes = Quiz.objects.all().order_by('-times_taken')
    i = 0
    while i < len(quizzes):
        if quizzes[i] == quiz:
            return i + 1
        else:
            i += 1
