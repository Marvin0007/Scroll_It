from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='Home'),
    path('tweets', views.tweet_list, name ='Details'),
    path('tweets/create', views.create_tweet, name='Create'),
    path('tweets/<int:tweet_id>', views.tweet_detail , name='Tweets'),
    path('api/tweets/<int:tweet_id>/delete', views.tweet_delete, name='Delete'),
    path('api/tweets/action', views.tweet_delete, name = 'Delete')
]