from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import re
import uuid

from orders.models import Order
from . import easypay

# Test card numbers for the sandbox simulator (no real money moves).
TEST_SUCCESS_CARD = '4242424242424242'
TEST_DECLINE_CARD = '4000000000000002'


def _luhn_ok(number):
    digits = [int(d) for d in number if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


@login_required
def easypaisa_start(request, order_id):
    """Send the customer to Easypaisa's secure payment page.

    With real merchant credentials configured this auto-submits a signed
    form to Easypay. Without them (test setup) it shows the local sandbox
    simulator page instead — clearly labelled, no real money moves.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_status == 'paid':
        return redirect('order_confirmation', order_id=order.id)
    if order.payment_method != 'easypaisa':
        messages.warning(request, 'This order is not an Easypaisa order.')
        return redirect('order_detail', order_id=order.id)

    post_back_url = request.build_absolute_uri(
        reverse('payments:easypaisa_callback'))
    payload = easypay.build_payload(order, post_back_url)

    if easypay.is_configured():
        return render(request, 'payments/redirect.html', {
            'order': order,
            'checkout_url': easypay.checkout_url(),
            'payload': payload,
        })
    # Test setup: no merchant credentials yet — use the simulator.
    return render(request, 'payments/simulator.html', {
        'order': order,
        'payload': payload,
    })


@login_required
@require_POST
def easypaisa_simulate(request, order_id):
    """Sandbox simulator: mimics Easypaisa's secure payment page.

    Only available while no real merchant credentials are configured.
    A valid test payment succeeds; a wrong card number / CVV is declined
    with a clear message — exactly like the real gateway would.
    """
    if easypay.is_configured():
        return redirect('easypaisa_start', order_id=order_id)
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.payment_status == 'paid':
        return redirect('order_confirmation', order_id=order.id)

    method = request.POST.get('pay_method', 'wallet')
    success, desc = False, ''
    if method == 'card':
        card = re.sub(r'\D', '', request.POST.get('card_number', ''))
        cvv = request.POST.get('cvv', '').strip()
        expiry = request.POST.get('expiry', '').strip()
        if not card or not _luhn_ok(card):
            desc = 'Invalid card number. Please check the number and try again.'
        elif not re.fullmatch(r'\d{3,4}', cvv):
            desc = 'Invalid CVV. The CVV is the 3-digit code on the back of your card.'
        elif not re.fullmatch(r'(0[1-9]|1[0-2])/\d{2}', expiry):
            desc = 'Invalid expiry date. Use MM/YY format.'
        elif card == TEST_DECLINE_CARD:
            desc = 'Your card was declined. Please check your card details or try another card.'
        else:
            success, desc = True, 'Success. Transaction completed.'
    else:  # Easypaisa wallet (mobile number + OTP on the real page)
        mobile = re.sub(r'\D', '', request.POST.get('mobile_number', ''))
        if not re.fullmatch(r'03\d{9}', mobile):
            desc = 'Invalid Easypaisa mobile number. Enter an 11-digit number starting with 03.'
        else:
            success, desc = True, 'Success. Transaction completed.'

    code = '0000' if success else '9999'
    data = easypay.sign_callback_response(order.order_number, code, desc)
    data['transactionId'] = f"SIM-{uuid.uuid4().hex[:10].upper()}"
    return render(request, 'payments/callback_form.html', {
        'order': order,
        'callback_url': request.build_absolute_uri(
            reverse('payments:easypaisa_callback')),
        'data': data,
        'success': success,
    })


@csrf_exempt
def easypaisa_callback(request):
    """Easypaisa posts the payment result here (postBackURL).

    The response hash is verified before the order is trusted. A success
    (responseCode 0000) marks the order paid; anything else — wrong card,
    wrong CVV, declined, cancelled — marks it failed and shows a clear
    error page. No card number or CVV ever reaches this view.
    """
    data = request.POST if request.method == 'POST' else request.GET
    order_ref = data.get('orderRefNumber') or data.get('orderRefNum')
    if not order_ref:
        return HttpResponseBadRequest('Missing order reference.')
    order = Order.objects.filter(order_number=order_ref).first()
    if not order:
        return HttpResponseBadRequest('Order not found.')

    if not easypay.verify_callback(data):
        # Never trust an unverified callback.
        return render(request, 'payments/failed.html', {
            'order': order,
            'error_message': 'We could not verify this payment with Easypaisa. '
                             'No money has been taken. Please try again or choose '
                             'Cash on Delivery.',
        }, status=400)

    if order.payment_status == 'paid':
        return redirect('order_confirmation', order_id=order.id)

    response_code = data.get('responseCode', '')
    if response_code == '0000':
        order.payment_status = 'paid'
        order.status = 'processing'
        order.payment_reference = data.get('transactionId', '') or order_ref
        order.save(update_fields=['payment_status', 'status', 'payment_reference'])
        messages.success(
            request,
            f'Payment successful! Order #{order.order_number} is confirmed.')
        return redirect('order_confirmation', order_id=order.id)

    order.payment_status = 'failed'
    order.save(update_fields=['payment_status'])
    desc = (data.get('responseDesc') or '').strip()
    error_message = (
        f'Your payment was not completed. {desc} '
        'No money was deducted. Please check your card number and CVV '
        'and try again, or choose Cash on Delivery.' if desc else
        'Your payment was not completed. No money was deducted. '
        'Please check your card number and CVV and try again, '
        'or choose Cash on Delivery.')
    return render(request, 'payments/failed.html', {
        'order': order,
        'error_message': error_message,
        'gateway_message': desc,
    })
