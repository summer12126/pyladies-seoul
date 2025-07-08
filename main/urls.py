from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("events/", views.events_list, name="events_list"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("contribute/", views.contribute, name="contribute"),
    path("faq/", views.faq, name="faq"),
    path("coc/", views.coc, name="coc"),
    path("health/", views.health_check, name="health_check"),
]
