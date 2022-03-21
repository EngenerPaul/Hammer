import random
import string
import time

from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect

from .forms import EnterPhoneForm, LoginCodeForm, EnterRefCodeForm
from .models import Hammer_User


def get_referral_code(ref_codes, length=6):
    while True:
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, length))
        if rand_string not in ref_codes:
            return rand_string


def get_confirm_code():
    return random.randint(1000, 9999)


def send_sms():
    time.sleep(1)
    return get_confirm_code()


class CustomLoginView(TemplateView, FormMixin):
    template_name = 'referral/login.html'
    form_class = EnterPhoneForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            phone = form.cleaned_data.get('phone')
            request.session['phone'] = phone
            request.session['code'] = send_sms()
            return redirect('login_code_page')
        else:
            return self.form_invalid(form)


class CustomLoginViewConfirm(TemplateView, FormMixin):
    template_name = 'referral/logincode.html'
    form_class = LoginCodeForm
    success_url = reverse_lazy('home_page')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            code = form.cleaned_data.get('code')
            if code == str(request.session['code']):
                return self.form_valid(request, form)
            else:
                messages.error(self.request, 'Wrong code')
                return HttpResponseRedirect(reverse_lazy('login_code_page'))
        else:
            return self.form_invalid(form)

    def form_valid(self, request, form):
        hammer_users = Hammer_User.objects.values_list('phone',
                                                       'personal_code')
        phone_numbers = []
        referral_codes = []
        for item in hammer_users:
            phone_numbers.append(item[0])
            referral_codes.append(item[1])
        session_phone = request.session['phone']

        if int(session_phone) not in phone_numbers:
            hammer_User = Hammer_User()
            hammer_User.phone = request.session['phone']
            hammer_User.personal_code = get_referral_code(referral_codes)
            hammer_User.save()
        return super().form_valid(form)


class HomeView(TemplateView):
    template_name = 'referral/home.html'


class ProfileView(TemplateView, FormMixin):
    template_name = 'referral/profile.html'
    form_class = EnterRefCodeForm

    def get(self, request, *args, **kwargs):
        if request.session.get('phone'):
            return super().get(request, *args, **kwargs)
        else:
            return redirect('login_page')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            all_codes = Hammer_User.objects.values_list('personal_code')
            all_codes = [i[0] for i in all_codes]
            ref_code = form.cleaned_data.get('strange_code')
            user = Hammer_User.objects.get(
                phone=self.request.session.get('phone'))
            if (ref_code in all_codes) and (ref_code != user.personal_code):
                return self.form_valid(ref_code, user)
            else:
                messages.error(self.request, 'Wrong code')
                return HttpResponseRedirect(reverse_lazy('profile_page'))
        else:
            return self.form_invalid(form)

    def form_valid(self, ref_code, user_prof):
        user_prof.referral_code = ref_code
        user_prof.save()
        return HttpResponseRedirect(reverse_lazy('profile_page'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_phone'] = self.request.session.get('phone')
        user_info = Hammer_User.objects.get(phone=context['my_phone'])
        context['my_code'] = user_info.personal_code
        context['strange_ref_code'] = user_info.referral_code
        context['partners'] = Hammer_User.objects.filter(
            referral_code=context['my_code']).values('phone')
        return context


def logout(request, *args, **kwargs):
    print('logout works')
    request.session.clear()
    return redirect('login_page')
