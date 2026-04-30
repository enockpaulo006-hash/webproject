from django.urls import path

from .views import my_orders_view, order_create_view, received_requests_view

app_name = "orders"

urlpatterns = [
    path("create/<int:product_id>/", order_create_view, name="create"),
    path("my-orders/", my_orders_view, name="my_orders"),
    path("received-requests/", received_requests_view, name="received_requests"),
]
