from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductForm, ProductFormSet
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
        formset = ProductFormSet(request.POST, request.FILES, prefix="products")
        if formset.is_valid():
            created_products = 0

            for form in formset:
                if not form.cleaned_data:
                    continue

                product = form.save(commit=False)
                product.seller = request.user
                product.save()
                created_products += 1

            if created_products == 1:
                messages.success(request, "Your product has been posted successfully.")
            else:
                messages.success(
                    request,
                    f"{created_products} products have been posted successfully.",
                )
            return redirect("products:my_products")
    else:
        formset = ProductFormSet(prefix="products")

    return render(request, "products/product_form.html", {"formset": formset})


@login_required
def my_products_view(request):
    products = Product.objects.filter(seller=request.user).order_by("-created_at")
    return render(request, "products/my_products.html", {"products": products})


@login_required
def product_update_view(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Your product has been updated successfully.")
            return redirect("products:my_products")
    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_edit.html", {"form": form, "product": product})


@login_required
@require_POST
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    product_title = product.title
    product.delete()
    messages.success(request, f'"{product_title}" has been deleted successfully.')
    return redirect("products:my_products")
