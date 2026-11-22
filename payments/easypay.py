"""
Easypay (Easypaisa Merchant Services) hosted-checkout integration.

Flow
----
1. Checkout creates the order with payment_method='easypaisa' and
   payment_status='pending', then redirects to payments:easypaisa_start.
2. We build a signed payload and POST the customer to Easypaisa's secure
   hosted payment page (sandbox or live). The customer enters their
   Easypaisa wallet number / OTP — or card details — ONLY on Easypaisa's
   page. Our site never sees, collects or stores card numbers or CVV.
3. Easypaisa POSTs the result to our callback URL (postBackURL). We verify
   the response hash before trusting it, mark the order paid/failed and
   send the customer to the confirmation or the failed page.

Notes
-----
* Easypaisa issues sandbox credentials per merchant (Store ID + Hash Key)
  — there are no public demo credentials. Until real (or sandbox) merchant
  credentials are configured in the environment, the integration runs in
  "test setup" mode: checkout redirects to a clearly-labelled local
  simulator page that mimics Easypaisa's secure page so the full flow
  (success + wrong card/CVV failure) can be tested end-to-end with no
  real money moving.
* Easypay's classic hosted checkout covers Easypaisa Mobile Account (MA)
  wallet payments and OTC vouchers. Direct card acquiring is a separate
  Easypaisa/acquirer product — if the merchant later enables cards, the
  card is still entered on Easypaisa's hosted page, never on this site.
* Endpoints / signing format follow Easypay's Merchant Services docs
  (sandbox: easypaystg.easypaisa.com.pk, live: easypay.easypaisa.com.pk).
  The hash field order is documented by Easypaisa and must match exactly;
  if Easypaisa changes it, the '-27 hash mismatch' error appears and the
  order in _request_hash_string / _response_hash_string must be updated
  from the latest merchant PDF.

Environment variables (see .env.example):
    EASYPAY_STORE_ID     Store ID issued by Easypaisa
    EASYPAY_HASH_KEY     Hash Key issued by Easypaisa (HMAC-SHA256)
    EASYPAY_ACCOUNT_NO   Merchant account number (optional, settlement)
    EASYPAY_SANDBOX      'True' (default) = sandbox, 'False' = live
"""
import base64
import hashlib
import hmac

from django.conf import settings

SANDBOX_URL = 'https://easypaystg.easypaisa.com.pk/easypay/Index.jsf'
LIVE_URL = 'https://easypay.easypaisa.com.pk/easypay/Index.jsf'

PLACEHOLDER_STORE_ID = 'YOUR_EASYPAY_STORE_ID'
PLACEHOLDER_HASH_KEY = 'YOUR_EASYPAY_HASH_KEY'


def get_config():
    """Easypay settings from the environment (never hardcoded)."""
    return {
        'store_id': getattr(settings, 'EASYPAY_STORE_ID', '') or '',
        'hash_key': getattr(settings, 'EASYPAY_HASH_KEY', '') or '',
        'account_no': getattr(settings, 'EASYPAY_ACCOUNT_NO', '') or '',
        'sandbox': getattr(settings, 'EASYPAY_SANDBOX', True),
    }


def is_configured():
    """True only when real merchant credentials are present."""
    cfg = get_config()
    return bool(cfg['store_id'] and cfg['store_id'] != PLACEHOLDER_STORE_ID
                and cfg['hash_key'] and cfg['hash_key'] != PLACEHOLDER_HASH_KEY)


def checkout_url():
    return SANDBOX_URL if get_config()['sandbox'] else LIVE_URL


def _hmac_base64(message, key):
    digest = hmac.new(key.encode('utf-8'), message.encode('utf-8'),
                      hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')


def _request_hash_string(payload):
    # Field order is fixed by Easypay — do not reorder.
    return (
        f"amount={payload['transactionAmount']}"
        f"&postBackURL={payload['postBackURL']}"
        f"&orderRefNum={payload['orderRefNum']}"
        f"&storeId={payload['storeId']}"
        f"&transactionType={payload['transactionType']}"
    )


def build_payload(order, post_back_url):
    """Signed payload for the Easypay hosted checkout form."""
    cfg = get_config()
    amount = f"{float(order.total_amount):.2f}"
    payload = {
        'storeId': cfg['store_id'],
        'orderRefNum': order.order_number,
        'transactionAmount': amount,
        'postBackURL': post_back_url,
        'mobileAccountNo': '',
        'emailAddr': order.email,
        'transactionType': 'MA',
        'tokenExpiry': '',
        'bankIdentificationNumber': '',
        'encryptedHashRequest': '',
        'merchantPaymentMethod': '',
    }
    payload['merchantHashedReq'] = _hmac_base64(
        _request_hash_string(payload), cfg['hash_key'])
    return payload


def _response_hash_string(data):
    # Field order is fixed by Easypay — do not reorder.
    return (
        f"orderRefNumber={data.get('orderRefNumber', '')}"
        f"&responseCode={data.get('responseCode', '')}"
        f"&responseDesc={data.get('responseDesc', '')}"
        f"&storeId={data.get('storeId', '')}"
    )


def verify_callback(data):
    """Check Easypaisa's response hash. Returns True if it matches.

    In test-setup mode (placeholder credentials) the local simulator signs
    with the same placeholder key, so verification works identically.
    """
    cfg = get_config()
    expected = _hmac_base64(_response_hash_string(data), cfg['hash_key'])
    received = (data.get('merchantHashedResp') or '').strip()
    return bool(received) and hmac.compare_digest(expected, received)


def sign_callback_response(order_ref, response_code, response_desc):
    """Build a signed callback payload (used by the sandbox simulator)."""
    cfg = get_config()
    data = {
        'orderRefNumber': order_ref,
        'responseCode': response_code,
        'responseDesc': response_desc,
        'storeId': cfg['store_id'],
    }
    data['merchantHashedResp'] = _hmac_base64(
        _response_hash_string(data), cfg['hash_key'])
    return data
