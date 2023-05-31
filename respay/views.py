from rest_framework import status
from django.http import HttpResponse, HttpResponseRedirect
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from . models import *
from . serializers import *
from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
User = get_user_model()
# Create your views here.

API_URL = "http/localhost:8000/media/"
stripe.api_key = settings.STRIPE_SECRET_KEY
# stripe.api_key = 'sk_test_51LQs56J4Ld6rviALOVsWWWhfb6WOhNpPpc7xwoTvyYTSEkVXlNephzKfJwG90oYm9WoqbdLT8v29cHqWki7uB4PW004CH6Kg9S'


class ProductPreview(RetrieveAPIView):
    serializer_class = ResProductSerializer
    permission_classes = [permissions.AllowAny]
    queryset = ResProduct.objects.all()


class CreateCheckOutSession(APIView):

    # def get(self, request, *args, **kwargs):
    #     prod_id = self.kwargs["pk"]
    #     product = ResProduct.objects.get(id=prod_id)
    #     print('=>  ', product)
    #     return Response()

    def post(self, request, *args, **kwargs):
        prod_id = self.kwargs["pk"]
        try:
            product = ResProduct.objects.get(id=prod_id)
            print('MEEEEE    ', product)
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': int(product.price) * 100,
                            'product_data': {
                                'name': product.name,
                                'images': [f"{API_URL}/{product.product_image}"]

                            }
                        },
                        'quantity': 1,
                    },
                ],
                metadata={
                    "product_id ": product.id
                },
                mode='payment',
                success_url=settings.SITE_URL + '?success=true',
                # success_url=settings.FRONTEND_WEBSITE_SUCCESS_URL,
                # cancel_url=settings.FRONTEND_WEBSITE_CANCEL_URL
                cancel_url=settings.SITE_URL + '?canceled=true',
            )
            return redirect(checkout_session.url)
        except Exception as e:
            return Response({'msg': 'something went wrong while creating stripe session', 'error': str(e)}, status=500)


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_SECRET_WEBHOOK
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        print(session)
        customer_email = session['customer_details']['email']
        prod_id = session['metadata']['product_id']
        product = ResProduct.objects.get(id=prod_id)
        # sending confimation mail
        send_mail(
            subject="payment sucessful",
            message=f"thank for your purchase your order is ready.  download url {product.book_url}",
            recipient_list=[customer_email],
            from_email="henry2techgroup@gmail.com"
        )

        # creating payment history
        # user=User.objects.get(email=customer_email) or None

        PaymentHistory.objects.create(product=product, payment_status=True)
    # Passed signature verification
    return HttpResponse(status=200)


# This is your test secret API key.
stripe.api_key = 'sk_test_51LQs56J4Ld6rviALOVsWWWhfb6WOhNpPpc7xwoTvyYTSEkVXlNephzKfJwG90oYm9WoqbdLT8v29cHqWki7uB4PW004CH6Kg9S'


class StripeCheckOutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price': 'price_1MgSVBJ4Ld6rviALW6VKsgVL',
                        'quantity': 1,
                    },
                ],
                payment_method_types=['card',],
                mode='payment',
                success_url=settings.SITE_URL +
                '/?success=true&session_id={CHECKOUT_SESSION_ID}',
                cancel_url=settings.SITE_URL + '/?canceled=true',
            )
            return redirect(checkout_session.url)
        except:
            return Response(
                {'error': 'Something went wrong when creating stripe checkout session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
