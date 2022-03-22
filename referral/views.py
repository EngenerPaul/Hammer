import random
import string
import time

from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.hashers import make_password

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import EnterPhoneForm, LoginCodeForm, EnterRefCodeForm
from .models import User


def get_referral_code(ref_codes, length=6):
    """ Creating a distinct referral link """

    while True:
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, length))
        if rand_string not in ref_codes:
            return rand_string


def send_sms():
    """ Simulation of sms sending and creating confirmation code """

    time.sleep(1)
    return random.randint(1000, 9999)


class CustomLoginView(TemplateView, FormMixin):
    """ Dispatch sms code to phone and creating new object of the User model
    if it doesn't exist.
    is_active = False, confirm_code = None, username = password = phone """

    template_name = 'referral/login.html'
    form_class = EnterPhoneForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            phone = int(form.cleaned_data.get('phone'))
            code = send_sms()

            """ If phone is exist then we change code else create a new record
            in the DB """
            users = User.objects.values_list('username')
            users = [i[0] for i in users]

            if phone in users:
                user = User.objects.get(username=phone)
                user.confirm_code = code
                user.save()
            else:
                user = User()
                user.password = make_password(str(phone))
                user.last_login = None
                user.is_superuser = False
                user.username = phone
                user.email = ''
                user.is_staff = False
                user.is_active = False
                user.confirm_code = code
                user.personal_code = None
                user.referral_code = None
                user.save()

            request.session['phone'] = phone
            request.session['code'] = code
            return redirect('login_code_page')
        else:
            return self.form_invalid(form)


class CustomLoginViewConfirm(TemplateView, FormMixin):
    """ Confirmation of SMS code and activation of new user(phone) """

    template_name = 'referral/logincode.html'
    form_class = LoginCodeForm
    success_url = reverse_lazy('home_page')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            phone = request.session['phone']
            code = int(form.cleaned_data.get('code'))

            user = User.objects.get(username=phone)
            if code == user.confirm_code and user.confirm_code is not None:
                user.confirm_code = None
                if not user.is_active:
                    user.is_active = True
                    all_personal_codes = User.objects.values_list(
                        'personal_code')
                    all_personal_codes = [i[0] for i in all_personal_codes]
                    user.personal_code = get_referral_code(all_personal_codes)
                    # user.token = user.get_token
                user.save()
                request.session['is_auth'] = True
                return self.form_valid(request)
            else:
                messages.error(self.request, 'Wrong code')
                return HttpResponseRedirect(reverse_lazy('login_code_page'))
        else:
            return self.form_invalid(form)


class HomeView(TemplateView):
    """ Home page of any content """

    template_name = 'referral/home.html'


class ProfileView(TemplateView, FormMixin):
    """ Profile page """

    template_name = 'referral/profile.html'
    form_class = EnterRefCodeForm

    def get(self, request, *args, **kwargs):
        if request.session.get('is_auth'):
            return super().get(request, *args, **kwargs)
        else:
            return redirect('login_page')

    def post(self, request, *args, **kwargs):
        """ Setting a strange referral code """

        form = self.get_form()
        if form.is_valid():
            referral_code = form.cleaned_data.get('strange_code')
            user = User.objects.get(username=self.request.session.get('phone'))

            if user.referral_code:
                messages.error(
                    self.request, 'Your referral code already exists')
                return HttpResponseRedirect(reverse_lazy('profile_page'))
            all_referral_codes = User.objects.values_list('personal_code')
            all_referral_codes = [i[0] for i in all_referral_codes]
            if referral_code == '' or referral_code is None:
                messages.error(self.request, "Your code is empty")
                return HttpResponseRedirect(reverse_lazy('profile_page'))
            if referral_code not in all_referral_codes:
                messages.error(self.request, "This code doesn't exist")
                return HttpResponseRedirect(reverse_lazy('profile_page'))
            if referral_code == user.personal_code:
                messages.error(self.request, "It's your own code")
                return HttpResponseRedirect(reverse_lazy('profile_page'))

            user.referral_code = referral_code
            user.save()
            return HttpResponseRedirect(reverse_lazy('profile_page'))
        else:
            return self.form_invalid(form)

    def form_valid(self, ref_code, user_prof):
        user_prof.referral_code = ref_code
        user_prof.save()
        return HttpResponseRedirect(reverse_lazy('profile_page'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(username=self.request.session.get('phone'))
        context['my_phone'] = user.username
        context['my_code'] = user.personal_code
        context['strange_ref_code'] = user.referral_code
        context['partners'] = User.objects.filter(
            referral_code=user.personal_code).values('username')
        return context


def logout(request, *args, **kwargs):
    """ Logout """

    request.session.clear()
    return redirect('home_page')


#################################################################
#                            DRF API                            #
#################################################################


class LoginAPI(APIView):
    """ Return of a confirm code and creating new object of the User model
    if it doesn't exist.
    is_active = False, confirm_code = None, username = password = phone"""

    def get(self, request, phone):
        code = send_sms()

        """ If phone is exist than we change code else create a new record
        in the DB """
        users = User.objects.values_list('username')
        users = [i[0] for i in users]

        if phone in users:
            user = User.objects.get(username=phone)
            user.confirm_code = code
            user.save()
        else:
            user = User()
            user.password = make_password(str(phone))
            user.last_login = None
            user.is_superuser = False
            user.username = phone
            user.email = ''
            user.is_staff = False
            user.is_active = False
            user.confirm_code = code
            user.personal_code = None
            user.referral_code = None
            user.save()

        time.sleep(1)
        return Response({'phone': phone, 'code': code})


class LoginConfirmAPI(APIView):
    """ Confirmation of SMS code and activation of new user(phone) """

    def post(self, request):
        phone = request.data['username']
        code = request.data['code']

        user = User.objects.get(username=phone)
        if code == user.confirm_code and user.confirm_code is not None:
            user.confirm_code = None
            if not user.is_active:
                user.is_active = True
                all_personal_codes = User.objects.values_list('personal_code')
                all_personal_codes = [i[0] for i in all_personal_codes]
                user.personal_code = get_referral_code(all_personal_codes)
                user.token = user.get_token
            if user.token is None:
                user.token = user.get_token
            user.save()
            return Response({'token': user.token})
        else:
            return Response('Wrong code')


class ProfileAPI(APIView):
    """ Return all user informations by token """

    def post(self, request):
        token = request.data['token']
        user_token = User.objects.values_list('token')
        user_token = [i[0] for i in user_token]
        if token in user_token:
            user = User.objects.get(token=token)
            if user.referral_code:
                referral_code = user.referral_code
            else:
                referral_code = 'referral code is missing'
            strange_phone = User.objects.filter(
                referral_code=user.personal_code).values_list('username')
            strange_phone = [i[0] for i in strange_phone]
            return Response({
                'phone': user.username,
                'personal referral code': user.personal_code,
                'referral_code': referral_code,
                'partners': strange_phone
            })
        else:
            return Response('Wrong token')


class ChangeRefCode(APIView):
    """ Setting a strange referral code """

    def post(self, request):
        token = request.data['token']
        referral_code = request.data['referral code']

        user_token = User.objects.values_list('token')
        user_token = [i[0] for i in user_token]
        if token in user_token:
            user = User.objects.get(token=token)

            if user.referral_code:
                return Response('Your referral code already exists')
            all_referral_codes = User.objects.values_list('personal_code')
            all_referral_codes = [i[0] for i in all_referral_codes]
            if referral_code == '' or referral_code:
                return Response("Your code is empty")
            if referral_code not in all_referral_codes:
                return Response("This code doesn't exist")
            if referral_code == user.personal_code:
                return Response("It's your own code")

            user.referral_code = referral_code
            user.save()
            return Response(
                f'Referral code {referral_code} installed successfully'
            )
        else:
            return Response('Wrong token')
