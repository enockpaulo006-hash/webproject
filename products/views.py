from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Product


def product_list_view(request):
    products = Product.objects.filter(status="active").select_related("seller")
    return render(request, "products/product_list.html", {"products": products})


def product_detail_view(request, pk):
    product = get_object_or_404(Product.objects.select_related("seller"), pk=pk, status="active")
    return render(request, "products/product_detail.html", {"product": product})


@login_required
def product_create_view(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Your product has been posted successfully.")
            return redirect("products:my_products")
    else:
        form = ProductForm()

    return render(request, "products/product_form.html", {"form": form})


@login_required
def my_products_view(request):
    products = Product.objects.filter(seller=request.user).order_by("-created_at")
    return render(request, "products/my_products.html", {"products": products})
