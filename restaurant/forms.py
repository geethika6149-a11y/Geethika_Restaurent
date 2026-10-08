from django import forms
from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'customer_email', 'table_number', 'special_instructions']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 555-0199',
                'required': True
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com (optional)'
            }),
            'table_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Table # (1 - 50)',
                'min': '1',
                'max': '50',
                'required': True
            }),
            'special_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any dietary restrictions, allergies, or notes for the chef...'
            }),
        }

    def clean_table_number(self):
        table = self.cleaned_data.get('table_number')
        if table is None or table < 1 or table > 50:
            raise forms.ValidationError("Please provide a valid table number between 1 and 50.")
        return table


class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }


class OrderLookupForm(forms.Form):
    order_identifier = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter Order ID (e.g. 3) or Order Code (e.g. ORD-71D329)...',
            'required': True
        })
    )
