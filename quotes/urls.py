from django.urls import path

from . import views

app_name = "quotes"

urlpatterns = [
    path(
        "",
        views.quote_list,
        name="list",
    ),
    path(
        "generate/<int:service_id>/",
        views.quote_generate,
        name="generate",
    ),
    path(
        "<int:pk>/",
        views.quote_detail,
        name="detail",
    ),
]
