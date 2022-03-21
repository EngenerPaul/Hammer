from django.urls import path
from .views import CustomLoginView, CustomLoginViewConfirm, HomeView, \
                   ProfileView, logout

urlpatterns = [
    path('login', CustomLoginView.as_view(), name='login_page'),
    path('login_code', CustomLoginViewConfirm.as_view(),
         name='login_code_page'),
    path('home', HomeView.as_view(), name='home_page'),
    path('profile', ProfileView.as_view(), name='profile_page'),
    path('logout', logout, name='logout_url')
]
