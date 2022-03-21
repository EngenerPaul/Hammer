from django.shortcuts import redirect, render
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormMixin

from .forms import EnterPhoneForm, LoginCodeForm


class CustomLoginView(TemplateView, FormMixin):
    template_name = 'referral/login.html'
    form_class = EnterPhoneForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return redirect('logincode', phoneform=form)
        else:
            return self.form_invalid(form)


class CustomLoginViewConfirm(View):
    template_name = 'referral/logincode.html'
    form_class = LoginCodeForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(request, form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """If the form is valid, save the associated model."""

        self.object = form.save(commit=False)
        # Здесь мы присвоим значения всем полям в модели
        return super().form_valid(form)
