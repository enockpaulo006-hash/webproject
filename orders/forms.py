from django import forms

from .models import Order


class OrderRequestForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["buyer_phone", "order_message"]
        widgets = {
            "buyer_phone": forms.TextInput(attrs={"placeholder": "Enter your phone number"}),
            "order_message": forms.Textarea(attrs={"placeholder": "Write what you want to order", "rows": 5}),
        }
