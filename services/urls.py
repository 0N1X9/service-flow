from django.urls import path

from . import views

app_name = "services"

urlpatterns = [
    path("", views.service_list, name="list"),
    path("add/", views.service_create, name="add"),
    path("<int:pk>/edit/", views.service_update, name="edit"),
    path("<int:pk>/delete/", views.service_delete, name="delete"),
]
