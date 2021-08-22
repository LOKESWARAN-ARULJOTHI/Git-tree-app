from django.urls import path
from . import views
from .views import Home

# all urls in the app
urlpatterns = [
    path('', Home.as_view(), name="home"),
    path('number-of-trees-generated', views.no_of_trees)
]