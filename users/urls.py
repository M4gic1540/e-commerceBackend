from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from django.urls import path
from .views import LoginView, LogoutView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='usuarios')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
] + router.urls
