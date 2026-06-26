import json
import pickle
import random
import re
import datetime
import pandas as pd
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from .models import Student, Chat, Document, Rating
from rapidfuzz import fuzz
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Student
from .forms import StudentSignupForm
from django.shortcuts import render, redirect


BASE_DIR = Path(__file__).resolve().parent.parent

# ----------------------------------------------------------------------
# LOAD MODELS AND INTENTS
# ----------------------------------------------------------------------
print("\n" + "="*50)
print("LOADING CHATBOT MODEL...")
print("="*50)

model = None
vectorizer = None
dataset = None

try:
    model_path = BASE_DIR / 'chatbot' / 'model.pkl'
    vectorizer_path = BASE_DIR / 'chatbot' / 'vectorizer.pkl'
    model = pickle.load(open(model_path, 'rb'))
    vectorizer = pickle.load(open(vectorizer_path, 'rb'))
    print(f"✅ Model loaded: {model.classes_}")
except Exception as e:
    print(f"❌ Model error: {e}")

try:
    dataset_path = BASE_DIR / "dataset" / "oou_chatbot_dataset.xlsx"
    dataset = pd.read_excel(dataset_path)

    print(f"✅ Dataset loaded: {len(dataset)} questions")
    print(f"✅ Categories: {dataset['Category'].nunique()}")

except Exception as e:
    print(f"❌ Dataset Error: {e}")

print("="*50 + "\n")

# ----------------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------------
def home(request):
    return render(request, 'chatbot/home.html')

from rapidfuzz import fuzz


def get_response(tag, message):
    """
    Finds the best matching question within the predicted category.
    """

    # Make sure dataset is loaded
    if dataset is None:
        return None

    # Keep only rows from the predicted category
    category_data = dataset[dataset["Category"] == tag]

    if category_data.empty:
        return None

    best_score = 0
    best_answer = None

    # Compare the user's question with every question in the category
    for _, row in category_data.iterrows():
        score = fuzz.token_sort_ratio(
            message.lower(),
            str(row["Question"]).lower()
        )

        if score > best_score:
            best_score = score
            best_answer = row["Answer"]

    print(f"Best Match Score: {best_score}%")

    # Only return an answer if similarity is high enough
    if best_score >= 60:
        return best_answer

    return None

def get_varied_response(tag, message):
    base_response = get_response(tag)
    if not base_response:
        return None
    if tag == "greeting":
        current_hour = datetime.datetime.now().hour
        if current_hour < 12:
            return f"Good morning! {base_response}"
        elif current_hour < 17:
            return f"Good afternoon! {base_response}"
        else:
            return f"Good evening! {base_response}"
    if tag == "fees" or tag == "payment":
        extras = [
            " Need help with the portal? I can guide you through it.",
            " Remember, late payments incur a 5% fee after the deadline.",
            " For installment plans, contact the finance office directly.",
            " You can also pay in person at the cashier's office."
        ]
        return base_response + random.choice(extras)
    return base_response

def is_real_question(message):
    question_words = ['what','where','when','why','how','who','which','can','could','would','should','is','are','do','does','did']
    message_lower = message.lower()
    if '?' in message:
        return True
    words = message_lower.split()
    if words and words[0] in question_words:
        return True
    question_patterns = ['tell me', 'i want to know', 'i need to know', 'explain', 'describe', 'help me']
    if any(pattern in message_lower for pattern in question_patterns):
        return True
    if len(words) > 5:
        return True
    return False

def is_simple_greeting(message):
    greetings = ['hi','hello','hey','hi there','hello there','hey there','good morning','good afternoon','good evening']
    message_lower = message.lower().strip()
    message_clean = re.sub(r'[^\w\s]', '', message_lower)
    return message_clean in greetings

def is_related_to_oou(message):
    """
    Return True if the message is about Olabisi Onabanjo University (OOU).
    Otherwise False – the bot will politely refuse.
    """
    message_lower = message.lower()
    
    # Direct OOU identifiers
    oou_keywords = [
        'olabisi onabanjo', 'oou', 'ago iwoye', 'olabisi onabanjo university',
        'oou student', 'oou portal', 'oou fees', 'oou admission',
        'oou library', 'oou courses', 'oou campus', 'oou help desk',
        'oou registration', 'oou academic calendar', 'oou scholarship',
        'faculty of', 'department of', 'oou lecture', 'oou exam'
    ]
    if any(keyword in message_lower for keyword in oou_keywords):
        return True
    
    # Clearly unrelated topics (weather, sports, politics, entertainment, etc.)
    unrelated_topics = [
        'weather', 'covid', 'trump', 'biden', 'election', 'football match', 
        'nba', 'recipe', 'stock market', 'bitcoin', 'crypto', 'movie', 
        'game of thrones', 'nintendo', 'ps5', 'xbox', 'celebrity'
    ]
    if any(topic in message_lower for topic in unrelated_topics):
        return False
    
    # Educational terms that are plausible OOU‑related (even if user omitted "OOU")
    edu_terms = [
        'admission', 'fees', 'library', 'course', 'registration', 'scholarship',
        'campus', 'lecture', 'exam', 'result', 'transcript', 'hostel',
        'accommodation', 'student', 'department', 'faculty', 'tuition',
        'application', 'deadline', 'matriculation', 'convocation'
    ]
    if any(term in message_lower for term in edu_terms):
        return True
    
    # Very short messages (greetings, thanks, etc.) – allow, they are conversational
    if len(message_lower.split()) <= 3:
        return True
    
    # If nothing matched, assume off‑topic
    return False

def openai_fallback(message):
    """Call OpenAI with OOU‑only instruction."""
    try:
        response_ai = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Olabisi Onabanjo University (OOU), Nigeria. Only answer questions related to OOU – admissions, fees, courses, campus, library, student services, etc. If a question is not about OOU, politely say you cannot answer it and remind the user to ask OOU‑related questions."},
                {"role": "user", "content": message}
            ],
            max_tokens=250,
            temperature=0.7
        )
        return response_ai.choices[0].message.content
    except Exception as ai_error:
        print(f"❌ OpenAI Error: {ai_error}")
        return "I'm having trouble connecting. Please try again or contact the OOU help desk directly."

# ----------------------------------------------------------------------
# MAIN CHATBOT VIEW (with OOU filter)
# ----------------------------------------------------------------------
@csrf_exempt
@login_required
def chatbot_response(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    message = request.POST.get('message', '').strip()
    if not message:
        return JsonResponse({'response': 'Please enter a message.'})
    
    # ---- OOU‑ONLY FILTER ----
    if not is_related_to_oou(message):
        refusal = (
            "I'm here to assist only with questions related to Olabisi Onabanjo University (OOU). "
            "Please ask about admissions, fees, courses, library, campus services, or other OOU matters. "
            "For unrelated topics, I cannot provide answers."
        )
        # Save refusal to chat history (optional)
        try:
            chat_obj = Chat.objects.create(
                user=request.user if request.user.is_authenticated else None,
                message=message,
                response=refusal
            )
            return JsonResponse({'response': refusal, 'chat_id': chat_obj.id})
        except Exception:
            return JsonResponse({'response': refusal})
    # ---- END FILTER ----
    
    # If ML components missing, fallback to OpenAI (which also respects OOU rule)
    if model is None or vectorizer is None:
        response = openai_fallback(message)
        try:
            chat_obj = Chat.objects.create(
                user=request.user if request.user.is_authenticated else None,
                message=message,
                response=response
            )
            return JsonResponse({'response': response, 'chat_id': chat_obj.id})
        except Exception:
            return JsonResponse({'response': response})
    
    try:
        # ML prediction
        X = vectorizer.transform([message])
        prediction = model.predict(X)[0]
        confidence = max(model.predict_proba(X)[0])
        
        print(f"\n--- New Message ---")
        print(f"Message: {message}")
        print(f"Prediction: {prediction}, Confidence: {confidence:.2%}")
        
           # Decide to use OpenAI or ML
        use_openai = False
        reason = ""

        if confidence < 0.5:
            use_openai = True
            reason = f"Low confidence ({confidence:.2%})"

        elif is_real_question(message) and prediction == "greeting":
            use_openai = True
            reason = "Question misclassified as greeting"

        elif not get_response(prediction, message):
            use_openai = True
            reason = "No matching answer found in dataset"

        if is_simple_greeting(message) and prediction == "greeting":
            use_openai = False
            reason = "Simple greeting - using ML"

        if use_openai:
            print(f"🎯 Using OpenAI - Reason: {reason}")
            response = openai_fallback(message)
        else:
            response = get_response(prediction, message)

            if response is None:
                response = openai_fallback(message)

            print(f"✅ Using Dataset Response: {response[:100]}...")

        # Save chat with user context and get ID
        chat_obj = Chat.objects.create(
            user=request.user if request.user.is_authenticated else None,
            message=message,
            response=response
        )

        return JsonResponse({
            'response': response,
            'chat_id': chat_obj.id
        })
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'response': "An error occurred. Please try again."}, status=500)

# ----------------------------------------------------------------------
# FILE UPLOAD VIEW (requires login)
# ----------------------------------------------------------------------
@csrf_exempt
@login_required
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        description = request.POST.get('description', '')
        allowed_types = ['application/pdf', 'application/msword',
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                         'text/plain', 'image/jpeg', 'image/png']
        if uploaded_file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'error': 'File type not allowed.'}, status=400)
        if uploaded_file.size > 10 * 1024 * 1024:
            return JsonResponse({'success': False, 'error': 'File too large (max 10MB).'}, status=400)
        doc = Document.objects.create(
            user=request.user,
            file=uploaded_file,
            description=description
        )
        return JsonResponse({
            'success': True,
            'message': f'File "{uploaded_file.name}" uploaded successfully.',
            'file_url': doc.file.url
        })
    return JsonResponse({'success': False, 'error': 'No file provided.'}, status=400)

# ----------------------------------------------------------------------
# RATING VIEW (now saves to database)
# ----------------------------------------------------------------------
@csrf_exempt
def rate_message(request):
    if request.method == 'POST':
        message_id = request.POST.get('message_id')
        rating_value = request.POST.get('rating')
        try:
            # Try to get the Chat object by ID
            chat = Chat.objects.get(id=message_id)
            # Save rating on the Chat model
            chat.rating = rating_value
            chat.save()
            # Also create a Rating record
            Rating.objects.create(chat=chat, rating=rating_value)
            print(f"📊 Chat {message_id} rated as: {rating_value}")
            return JsonResponse({'success': True, 'message': 'Thank you for your feedback!'})
        except Chat.DoesNotExist:
            print(f"⚠️ Chat {message_id} not found for rating")
            return JsonResponse({'success': False, 'error': 'Chat message not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# ----------------------------------------------------------------------
def dashboard(request):

    if not request.user.is_authenticated:
        return redirect("admin_login")

    if not request.user.is_staff:
        return redirect("home")

    total_students = Student.objects.count()

    # Only administrators can access this page
    if not request.user.is_staff:
        return redirect("admin_login")

    total_students = Student.objects.count()

    total_chats = Chat.objects.count()

    total_documents = Document.objects.count()

    helpful = Rating.objects.filter(
        rating="helpful"
    ).count()

    not_helpful = Rating.objects.filter(
        rating="not-helpful"
    ).count()

    top_questions = (
        Chat.objects
        .values("message")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    recent_chats = (
        Chat.objects
        .select_related("user")
        .order_by("-created_at")[:10]
    )

    recent_students = (
        Student.objects
        .order_by("-created_at")[:10]
    )

    context = {

        "total_students": total_students,

        "total_chats": total_chats,

        "total_documents": total_documents,

        "helpful": helpful,

        "not_helpful": not_helpful,

        "top_questions": top_questions,

        "recent_chats": recent_chats,

        "recent_students": recent_students,

    }

    return render(
        request,
        "admin/dashboard.html",
        context
    )
# ----------------------------------------------------------------------
# DEBUG / TEST ENDPOINTS (unchanged)
# ----------------------------------------------------------------------
@csrf_exempt
def test_openai(request):
    if request.method == 'POST':
        message = request.POST.get('message', 'Hello')
        response = openai_fallback(message)
        return JsonResponse({'success': True, 'response': response, 'message': message})

@csrf_exempt
def test_ml_only(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if model is None or vectorizer is None:
            return JsonResponse({'error': 'Model not loaded'}, status=500)
        X = vectorizer.transform([message])
        prediction = model.predict(X)[0]
        confidence = max(model.predict_proba(X)[0])
        response = get_response(prediction)
        return JsonResponse({
            'success': True,
            'message': message,
            'prediction': prediction,
            'confidence': float(confidence),
            'response': response if response else "No response found",
            'available_categories': model.classes_.tolist()
        })

@csrf_exempt
def check_intent(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if model is None or vectorizer is None:
            return JsonResponse({'error': 'Model not loaded'}, status=500)
        X = vectorizer.transform([message])
        prediction = model.predict(X)[0]
        confidence = max(model.predict_proba(X)[0])
        all_probs = model.predict_proba(X)[0]
        top_indices = all_probs.argsort()[-3:][::-1]
        top_predictions = []
        for idx in top_indices:
            top_predictions.append({
                'intent': model.classes_[idx],
                'confidence': float(all_probs[idx])
            })
        return JsonResponse({
            'message': message,
            'predicted_intent': prediction,
            'confidence': float(confidence),
            'top_predictions': top_predictions,
            'is_question': is_real_question(message),
            'is_greeting': is_simple_greeting(message),
            'ml_response': get_response(prediction)
        })

@csrf_exempt
def health_check(request):
    return JsonResponse({
        'model_loaded': model is not None,
        'vectorizer_loaded': vectorizer is not None,
        'dataset_loaded': dataset is not None,
        'num_categories': len(model.classes_) if model else 0,
        'openai_configured': OPENAI_API_KEY != "your-api-key-here"
    })

def signup_view(request):

    if request.method == "POST":

        matric = request.POST.get("matric_number").upper().strip()
        surname = request.POST.get("surname").strip()

        if Student.objects.filter(matric_number=matric).exists():

            return render(request,
                          "chatbot/signup.html",
                          {
                              "error": "Matric number already exists."
                          })

        username = matric

        password = surname.lower()

        user = User.objects.create_user(
            username=username,
            password=password
        )

        Student.objects.create(
            user=user,
            matric_number=matric,
            surname=surname
        )

        login(request, user)

        return redirect("home")

    return render(request, "chatbot/signup.html")

def login_view(request):

    if request.method == "POST":

        matric = request.POST.get("matric_number").upper().strip()
        surname = request.POST.get("surname").lower().strip()

        user = authenticate(
            request,
            username=matric,
            password=surname
        )

        if user is not None:

            login(request, user)

            return redirect("home")

        return render(
            request,
            "chatbot/login.html",
            {
                "error": "Invalid Matric Number or Surname."
            }
        )

    return render(request, "chatbot/login.html")

def logout_view(request):

    logout(request)

    return redirect("login")

def admin_login(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login(request, user)

            return redirect("dashboard")

        return render(
            request,
            "admin/login.html",
            {
                "error": "Invalid administrator credentials."
            }
        )

    return render(request, "admin/login.html")