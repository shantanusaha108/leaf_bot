from django.urls import path
from .views import DiagnoseView
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html"), name="home"),
    path('api/diagnose/', DiagnoseView.as_view(), name='diagnose'),
]
