from cProfile import label
from django import forms


class EnterPhoneForm(forms.Form):
    phone = forms.CharField(
        label='Enter your phone number',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class LoginCodeForm(forms.Form):
    code = forms.CharField(
        label='Enter the received code',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
