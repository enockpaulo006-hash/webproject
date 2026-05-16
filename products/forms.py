from django import forms
from django.forms import formset_factory

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


ProductFormSet = formset_factory(
    ProductForm,
    extra=1,
    min_num=1,
    validate_min=True,
)
