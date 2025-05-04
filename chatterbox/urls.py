"""
URL configuration for chatterbox project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# chatterbox/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('post/new/', views.create_post, name='create_post'),
    path('comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
    path('post/<int:post_id>/<str:vote_type>/', views.vote_post, name='vote_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
    path('comment/<int:pk>/edit/', views.edit_comment, name='edit_comment'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('search/', views.search_view, name='search'),
    path('password-change/', auth_views.PasswordChangeView.as_view(), name='password_change'),

    # Password reset URLs
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='core/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='core/password_reset_complete.html'), name='password_reset_complete'),
]