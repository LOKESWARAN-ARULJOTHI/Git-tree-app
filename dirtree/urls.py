from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('number-of-trees-generated', views.no_of_trees)
]