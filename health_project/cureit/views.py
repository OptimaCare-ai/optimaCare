
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from django.core.mail import send_mail
from django.http import HttpResponseRedirect



def index(request):
    return render(request, 'index.html')

# Replace this with your actual OpenRouter API key
OPENROUTER_API_KEY = "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"





@csrf_exempt

def send_email(request):
    if request.method == 'POST':
        to_email = request.POST.get('email')
        symptoms = request.POST.get('symptoms')
        conditions = request.POST.get('conditions')
        urgency = request.POST.get('urgency')
        doctor = request.POST.get('doctor')
        medication = request.POST.get('medication')
        advice = request.POST.get('advice')

        subject = f"OptimaCare AI Diagnosis – {symptoms}"
        body = f"""
Hello,

Here are your AI-generated medical results from OptimaCare:

Symptoms: {symptoms}
Conditions: {conditions}
Urgency: {urgency}
Doctor Type: {doctor}
Medications: {medication}
Advice: {advice}

Take care,
– The OptimaCare Team
"""

        send_mail(subject, body, 'manpreetsingh88.msk@gmail.com', [to_email], fail_silently=False)

        return HttpResponseRedirect('/')


def ai_check(request):
    if request.method == 'POST':
        user_input = request.POST.get('symptoms', '')

        prompt = f"""
You are a medical reasoning AI.

The user says: "{user_input}"

Return the result in this exact JSON format:

{{
  "conditions": [list of likely conditions],
  "urgency": "emergency / see doctor / self-care",
  "doctor": "which specialist to consult",
  "medication": [list of basic suggestions],
  "advice": "short actionable advice",
  "location_search": "doctor or place to search on Google Maps"
}}
"""

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-3.5-turbo",  # You can change model here
                    "messages": [{"role": "user", "content": prompt}]
                }
            )

            # If status code is not 200, raise error
            if response.status_code != 200:
                raise Exception(f"API error: {response.status_code} - {response.text}")

            gpt_reply = response.json()["choices"][0]["message"]["content"]

            # Try to parse it as JSON
            data = json.loads(gpt_reply)

        except Exception as e:
            data = {
                "conditions": ["Could not generate conditions"],
                "urgency": "Unknown",
                "doctor": "General Physician",
                "medication": ["No suggestions"],
                "advice": str(e),
                "location_search": "clinic"
            }

        return render(request, 'ai_result.html', {
            'symptoms': user_input,
            'conditions': data.get("conditions", []),
            'urgency': data.get("urgency", "Unknown"),
            'doctor': data.get("doctor", "General Physician"),
            'medication': data.get("medication", []),
            'advice': data.get("advice", "No advice found."),
            'location_url': f"https://www.google.com/maps/search/{data.get('location_search', 'clinic').replace(' ', '+')}+near+me"
        })
