from datetime import timedelta

from click import style
from django import forms
from .models import RideModel
from django.utils.timezone import now

class NewRideForm(forms.ModelForm):
    class Meta:
        model = RideModel
        exclude = ['is_confirmed', 'owner', 'driver', 'share_user']
        VEHICLE_CHOICES = [('any','Any'),
                           ('suv','SUV'), 
                           ('pika','Pika'), 
                           ('van','Van'), 
                           ('sedan','Sedan'), 
                           ('sports_car','Sports car'), 
                           ('tank','Tank'), 
                           ('motorcycle','Motorcycle')]
        widgets = {
            'departure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter departure position'}),
            'destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter destination'}),
            'arrival_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'placeholder': 'Enter expected arrival time'},),
            'total_passenger': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter total number of passengers'}),
            'can_share': forms.CheckboxInput(attrs={'class': 'form-check-input', 'style': 'margin-left:2px; margin-top:6px;'}),
            'vehicle_type': forms.Select(attrs={'class': 'form-control'},choices=VEHICLE_CHOICES),
            'sp_info': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter special requirements (Optional)', 'style':'height:38px'}),
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_time = now()
        one_week_later = current_time + timedelta(days=7)
        min_time = current_time.strftime('%Y-%m-%dT%H:%M')
        max_time = one_week_later.strftime('%Y-%m-%dT%H:%M')
        # Set arrival time can only be within one weak
        self.fields['arrival_time'].widget.attrs['min'] = min_time
        self.fields['arrival_time'].widget.attrs['max'] = max_time
        self.fields['arrival_time'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        is_confirmed = cleaned_data.get('is_confirmed')
        departure = cleaned_data.get('departure')
        dest = cleaned_data.get('destination')
        total_passenger = cleaned_data.get('total_passenger')
        if is_confirmed:
            raise forms.ValidationError('You cannot revise a confirmed ride.')
        if dest == departure:
            raise forms.ValidationError({'destination': 'Destination and departure place cannot be the same.'})
        if total_passenger <= 0:
            raise forms.ValidationError({'total_passenger': 'Total passenger cannot be non positive number.'})
        return cleaned_data
