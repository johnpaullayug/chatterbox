from django.urls import path
from . import views
from .views import category_list, category_autocomplete
from django.contrib.auth import views as auth_views
from .views import CustomPasswordChangeView 

urlpatterns = [
    # ... your existing URLs ...
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('post/<int:post_id>/vote/<str:vote_type>/', views.vote_post, name='vote_post'),
    path('api/search/autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    path('search/', views.search_view, name='search'),
    path('categories/', category_list, name='category_list'),
    path('categories/autocomplete/', category_autocomplete, name='category_autocomplete'),
    path('profile/<str:username>/', views.profile_view, name='user_profile'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('api/posts/autocomplete/', views.post_autocomplete, name='post_autocomplete'),
    # ... other URLs ...
]


