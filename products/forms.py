from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "category",
            "price",
            "description",
            "image",
            "product_condition",
            "location",
        ]
