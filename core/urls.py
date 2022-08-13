from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('signup/', views.signup, name = 'signup'),
    path('signin/', views.signin, name = 'signin'),
    path('logout/', views.logout, name = 'logout'),
    path('upload/', views.upload, name = 'upload'),
    path('deletepost/<post_id>/', views.delete_post, name = 'delete_post'),
    path('likepost/<post_id>/', views.like_post, name = 'like_post'),
    path('profile/<str:pk>', views.profile, name = 'profile'),
    path('follow', views.follow, name = 'follow'),
    path('unfollow/<str:pk>', views.unfollow, name = 'unfollow'),
    path('search', views.search, name = 'search'),
    path('settings/', views.settings, name = 'settings'),
]
