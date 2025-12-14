# apps/users/urls.py
from django.urls import path
from .views import UserProfileView, UserListView # Import the new view

urlpatterns = [
    path('', UserListView.as_view(), name='user-list'), # New Endpoint
    path('me/', UserProfileView.as_view(), name='user-profile'),
]