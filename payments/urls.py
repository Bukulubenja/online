from django.urls import path

from . import views

urlpatterns = [
    path('checkout/<slug:slug>/', views.checkout, name='checkout'),
    path('payment/<int:payment_id>/confirm/', views.confirm_payment, name='confirm_payment'),
    path('payment/<int:payment_id>/receipt/', views.receipt, name='receipt'),
]
