from django.urls import path
from .views import CustomLoginView, CustomLoginViewConfirm

urlpatterns = [
    path('login', CustomLoginView.as_view(), name='login_page'),
]
