from django import forms
from django.contrib.auth import get_user_model
from .models import CarModel

User = get_user_model()

from django import forms
from .models import RSSUser, CaptchaModel

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        min_length=4,
        label='User name',
        error_messages={
            'required': 'Please enter user name.',
            'max_length': 'No more than 20 characters.',
            'min_length': 'No less than 4 characters.',
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    email = forms.EmailField(
        label='Email',
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Enter a valid email address.',
        },
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    captcha = forms.CharField(
        min_length=6,
        max_length=6,
        label='Captcha',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the captcha'
        })
    )
    pwd1 = forms.CharField(
        max_length=20,
        min_length=6,
        label='Password',
        error_messages={
            'required': 'Please enter password.',
            'max_length': 'No more than 20 characters.',
            'min_length': 'No less than 6 characters.',
        },
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    pwd2 = forms.CharField(
        max_length=20,
        min_length=6,
        label='Confirm Password',
        error_messages={
            'required': 'Please enter password once again to confirm.',
            'max_length': 'No more than 20 characters.',
            'min_length': 'No less than 6 characters.',
        },
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        exist = RSSUser.objects.filter(username=username).exists()
        if exist:
            raise forms.ValidationError('Account has already been registered.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        exist = RSSUser.objects.filter(email=email).exists()
        if exist:
            raise forms.ValidationError('Email has already been registered.')
        return email

    def clean_captcha(self):
        captcha = self.cleaned_data.get('captcha')
        email = self.cleaned_data.get('email')
        captcha_obj = CaptchaModel.objects.filter(email=email, captcha=captcha).first()
        if not captcha_obj:
            raise forms.ValidationError('Invalid captcha.')
        return captcha

    def clean_pwd2(self):
        pwd1 = self.cleaned_data.get('pwd1')
        pwd2 = self.cleaned_data.get('pwd2')
        if pwd1 != pwd2:
            raise forms.ValidationError('The two passwords are different.')
        return pwd2


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=20,
        min_length=4,
        label='User name',
        error_messages={'required': 'Please enter user name.'},
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    pwd = forms.CharField(
        max_length=20,
        min_length=6,
        label='Password',
        error_messages={'required': 'Please enter password.'},
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    remember = forms.BooleanField(
        required=False,
        label='Remember me',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class DriverRegisterForm(forms.Form):
    VEHICLE_CHOICES = [ ('suv','SUV'), 
                        ('pika','Pika'), 
                        ('van','Van'), 
                        ('sedan','Sedan'), 
                        ('sports_car','Sports car'), 
                        ('tank','Tank'), 
                        ('motorcycle','Motorcycle')
                        ]
    
    vehicle_type = forms.CharField(max_length=100,
                                   label='Vehicle Type',
                                   widget=forms.Select(attrs={'class': 'form-control'},choices=VEHICLE_CHOICES))
    vehicle_number = forms.CharField(max_length=100,
                                     label='License Plate Number',
                                     widget=forms.TextInput(attrs={
                                         'class': 'form-control',
                                         'placeholder': 'Enter License Plate Number'
                                     }))
    max_passenger = forms.IntegerField(label='Maximum Number of Passengers',
                                       widget=forms.NumberInput(attrs={
                                           'class': 'form-control',
                                           'placeholder': 'Enter maximum number of passenger'
                                       }))
    sp_info = forms.CharField(label='Special Vehicle Info',
                              required=False,
                              widget=forms.Textarea(
                                  attrs={
                                      'class': 'form-control',
                                      'placeholder': 'Enter special vehicle information (Optional)',
                                      'style': 'height:150px;',
                                  }
                              ))

    def clean_max_passenger(self):
        max_passenger = self.cleaned_data.get('max_passenger')
        if max_passenger <= 0:
            raise forms.ValidationError('Number of maximum passenger should not be non-positive number.')
        else:
            return max_passenger

class CarForm(forms.ModelForm):
    class Meta:
        model = CarModel
        exclude = ['user',]
        VEHICLE_CHOICES = [('suv','SUV'), 
                           ('pika','Pika'), 
                           ('van','Van'), 
                           ('sedan','Sedan'), 
                           ('sports_car','Sports car'), 
                           ('tank','Tank'), 
                           ('motorcycle','Motorcycle')]
        widgets = {
            'vehicle_type': forms.Select(attrs={'class': 'form-control'},choices=VEHICLE_CHOICES),
            'vehicle_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter vehicle number'}),
            'max_passenger': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter maximum passengers'}),
            'sp_info': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter special information (Optional)', 'style': 'height:150px;'}),
        }

    def clean_max_passenger(self):
        max_passenger = self.cleaned_data.get('max_passenger')
        if max_passenger <= 0:
            raise forms.ValidationError('Number of maximum passenger should not be a non-positive number.')
        return max_passenger
