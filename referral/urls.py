from django.urls import path
from .views import CustomLoginView, CustomLoginViewConfirm, HomeView, \
                   ProfileView, logout, \
                   LoginAPI, LoginConfirmAPI, ProfileAPI, ChangeRefCode


urlpatterns = [
    path('login', CustomLoginView.as_view(), name='login_page'),
    path('login_code', CustomLoginViewConfirm.as_view(),
         name='login_code_page'),
    path('', HomeView.as_view(), name='home_page'),
    path('profile', ProfileView.as_view(), name='profile_page'),
    path('logout', logout, name='logout_url'),

    path('user-api/login/<int:phone>', LoginAPI.as_view()),
    path('user-api/login/auth', LoginConfirmAPI.as_view()),
    path('user-api/profile', ProfileAPI.as_view()),
    path('user-api/change-ref-code', ChangeRefCode.as_view()),
]
