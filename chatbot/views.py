from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import ChatMessage, FAQ
from core.models import Product
import json

try:
    from groq import Groq
except ImportError:
    Groq = None

def chatbot_widget(request):
    return render(request, 'chatbot/widget.html')

@csrf_exempt
def chatbot_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key
    ChatMessage.objects.create(user=request.user if request.user.is_authenticated else None, session_id=session_id, message=user_message, is_user=True)
    response_text = _get_response(user_message.lower())
    ChatMessage.objects.create(user=request.user if request.user.is_authenticated else None, session_id=session_id, response=response_text, is_user=False)
    return JsonResponse({'response': response_text})

def _get_response(message: str) -> str:
    for faq in FAQ.objects.filter(is_active=True):
        for kw in faq.keywords.lower().split(','):
            if kw.strip() and kw.strip() in message:
                return faq.answer
    api_key = getattr(settings, 'GROQ_API_KEY', None)
    if Groq and api_key:
        try:
            products = Product.objects.filter(is_active=True)[:40]
            catalog = '\n'.join(f"- {p.name} (Rs.{p.final_price}): {p.short_description}" for p in products)
            system = f"""You are MediBot, the AI assistant for MyMedicine — a trusted online pharmacy in Pakistan.\n\nPolicies:\n- Delivery: 3-5 business days. Free on orders above Rs.2000.\n- Returns: Unopened products within 7 days.\n- Payment: Cash on Delivery & card.\n- Prescriptions reviewed by pharmacist within 24 hours.\n\nProducts:\n{catalog}\n\nRules:\n1. Be friendly, professional, concise (2-4 sentences).\n2. Never give medical diagnoses — say "Please consult a doctor."\n3. Only recommend products from catalog.\n4. Stay on-topic for MyMedicine only."""
            client = Groq(api_key=api_key)
            resp = client.chat.completions.create(model='llama3-8b-8192', messages=[{'role':'system','content':system},{'role':'user','content':message}], max_tokens=300)
            return resp.choices[0].message.content
        except Exception:
            pass
    if any(w in message for w in ['hello','hi','hey','salam']): return "Hi! 👋 I'm MediBot, MyMedicine's assistant. How can I help you today?"
    if any(w in message for w in ['order','track','delivery','ship']): return "📦 Track your order by going to My Orders. Delivery takes 3-5 business days. Free delivery on orders above Rs. 2,000!"
    if 'prescription' in message: return "📋 Upload your prescription at /upload-prescription/. Our pharmacist reviews it within 24 hours."
    if any(w in message for w in ['return','refund']): return "✅ Unopened products can be returned within 7 days. Email support@mymedicine.pk with your order number."
    if any(w in message for w in ['pay','payment','cash']): return "💳 We accept Cash on Delivery and simulated card payment. All prices include taxes."
    if any(w in message for w in ['contact','support','help']): return "📞 Reach us at support@mymedicine.pk or call 0800-MYMED-RX. Available Mon-Sat, 9am-6pm."
    if any(w in message for w in ['thank','thanks']): return "You're most welcome! 😊 Is there anything else I can help you with?"
    if any(w in message for w in ['doctor','symptom','disease']): return "🏥 For medical advice, please consult a licensed doctor. I can help with orders, products, and website queries."
    return "I'm not sure about that. Please contact us at support@mymedicine.pk or call 0800-MYMED-RX. Happy to help! 😊"
