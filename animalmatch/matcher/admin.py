from django.contrib import admin
from .models import Animal, Quiz, Answer

admin.site.register(Quiz)


class AnimalAdmin(admin.ModelAdmin):
    list_display = ("id", "image_url")
    search_fields = ["name"]


admin.site.register(Animal, AnimalAdmin)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'text')
    list_filter = ('question', 'text')
    search_fields = ('id', 'question', 'text')
    ordering = ['question']


admin.site.register(Answer, AnswerAdmin)
