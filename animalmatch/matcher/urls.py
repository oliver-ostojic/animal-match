from django.urls import path
from . import views

app_name = 'matcher'
urlpatterns = [
    # ex: /matcher/
    path("home/", views.home_view, name='home'),
    # ex: /matcher/quiz/0/
    path("quiz/<int:quiz_id>/", views.quiz_view, name='quiz'),
    # ex: /matcher/results/tree_frog/
    path("results/<str:animal_match>/", views.results_view, name='results'),
    # ex: matcher/error/some_error/400
    path("error/<str:e>/<int:status_code>/", views.error_view, name='error'),
    # ex: matcher/error/
    path("error/", views.error_view, name='error'),
    # ex: matcher/error/400
    path("error/<int:status_code>/", views.error_view, name='error'),
    # ex: matcher/error/some_error
    path("error/<str:e>/", views.error_view, name='error'),

]
