from django.urls import path
from .views import *
from django.views.decorators.csrf import csrf_exempt

app_name = 'respay'
urlpatterns = [

    path('create-stripe-checkout-session/',
         csrf_exempt(StripeCheckOutView.as_view())),
    # # path('stripe-webhook/', stripe_webhook_view, name='stripe-webhook'),
    # path('prd/<int:pk>/', ProductPreview.as_view(), name="product"),
    # path('create-checkout-session/<pk>/',
    #      csrf_exempt(CreateCheckOutSession.as_view()), name='checkout_session')
    # path('payment-with-stripe/', CustomPaymentEndpoint.as_view())
]
