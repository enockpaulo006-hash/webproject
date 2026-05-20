from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProductForm, ProductFormSet
from .models import Product


def product_list_view(request):
    query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "")

    products = Product.objects.filter(status="active").select_related("seller")

    if query:
        products = products.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
        )

    if selected_category:
        products = products.filter(category=selected_category)

    category_counts = {
        row["category"]: row["total"]
        for row in Product.objects.filter(status="active")
        .values("category")
        .annotate(total=Count("id"))
    }

    category_meta = {
        "electronics": {
            "icon": "💻",
            "subtitle": "Laptops, gadgets, and hardware",
        },
        "phones_accessories": {
            "icon": "📱",
            "subtitle": "Phones, chargers, and cases",
        },
        "books_notes": {
            "icon": "📚",
            "subtitle": "Textbooks, notes, and study guides",
        },
        "fashion": {
            "icon": "👗",
            "subtitle": "Clothing, shoes, and accessories",
        },
        "hostel_items": {
            "icon": "🏠",
            "subtitle": "Dorm supplies and room essentials",
        },
        "services": {
            "icon": "🛠️",
            "subtitle": "Tutoring, delivery, and repairs",
        },
        "other": {
            "icon": "🔖",
            "subtitle": "Unique finds and general listings",
        },
    }

    categories = []
    for code, label in Product.CATEGORY_CHOICES:
        categories.append(
            {
                "code": code,
                "label": label,
                "count": category_counts.get(code, 0),
                "icon": category_meta.get(code, {}).get("icon", "🔹"),
                "subtitle": category_meta.get(code, {}).get(
                    "subtitle", "Browse products by category"
                ),
            }
        )

    selected_category_label = None
    if selected_category:
        selected_category_label = next(
            (category["label"] for category in categories if category["code"] == selected_category),
            None,
        )

    context = {
        "products": products,
        "categories": categories,
        "query": query,
        "selected_category": selected_category,
        "selected_category_label": selected_category_label,
    }
    return render(request, "products/product_list.html", context)


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
