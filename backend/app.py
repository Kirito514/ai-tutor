# backend/app.py - Yangilangi asosiy fayl

from flask import Flask, request, jsonify, render_template
import json
import os
import sys

# Enhanced AI model'ni import qilish
try:
    from enhanced_ai_model import EnhancedAITutor
    AI_MODEL_AVAILABLE = True
    print("✅ Kengaytirilgan AI model import qilindi")
except ImportError as e:
    AI_MODEL_AVAILABLE = False
    print(f"⚠️ AI model import xatolik: {e}")
    print("💡 Oddiy mode'da ishlaymiz")

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')

# AI model instance
if AI_MODEL_AVAILABLE:
    try:
        ai_tutor = EnhancedAITutor()
        print("🚀 Kengaytirilgan AI yordamchi tayyor!")
    except Exception as e:
        print(f"❌ AI model yaratishda xatolik: {e}")
        ai_tutor = None
else:
    ai_tutor = None

# Fallback knowledge base (agar AI model ishlamasa)
fallback_knowledge = {
    "salom": "Salom! Men sizning AI ta'lim yordamchisizman. GPT-2 model bilan ishlayman!",
    "test": "Kengaytirilgan test tizimi! Qaysi mavzu: matematika, fizika, kimyo?",
    "ai": "Men sun'iy intellekt texnologiyasi bilan ishlayman. GPT-2 va web qidiruv qobiliyatim bor.",
    "internet": "Ha, men internet'dan ma'lumot qidira olaman! Yangi savollar bering.",
    "matematik": "Men murakkab matematik masalalarni yecha olaman: integral, differensial, matrisa...",
    "kuchli": "Endi men ancha kuchliman! GPT-2 model + web search + keng bilimlar bazasi!"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'anonymous')
        
        print(f"📝 Savol: {user_message}")  # Debug
        
        # Enhanced AI bilan javob
        if ai_tutor:
            response = ai_tutor.generate_response(user_message, user_id)
            confidence = 0.9
        else:
            # Fallback mode
            response = search_fallback_knowledge(user_message)
            confidence = 0.7
        
        print(f"✅ Javob: {response[:100]}...")  # Debug
        
        return jsonify({
            'response': response,
            'confidence': confidence,
            'ai_model': 'Enhanced GPT-2' if ai_tutor else 'Basic'
        })
        
    except Exception as e:
        print(f"❌ Chat xatolik: {e}")
        return jsonify({
            'response': f'Kechirasiz, xatolik yuz berdi: {str(e)}. Qayta urinib ko\'ring.',
            'error': str(e)
        }), 500

def search_fallback_knowledge(user_message):
    """Fallback bilimlar qidirish"""
    message_lower = user_message.lower()
    
    # To'liq mos kelish
    for keyword, answer in fallback_knowledge.items():
        if keyword in message_lower:
            return answer
    
    # Matematik amallar
    if '+' in user_message or 'plus' in message_lower:
        try:
            import re
            numbers = re.findall(r'\d+', user_message)
            if len(numbers) >= 2:
                result = sum(int(n) for n in numbers)
                return f"Javob: {' + '.join(numbers)} = {result}"
        except:
            pass
    
    return "AI model yuklanmadi. Asosiy savollarni javob bera olaman: salom, test, matematik amallar."

@app.route('/api/quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.get_json()
        topic = data.get('topic', 'matematika')
        difficulty = data.get('difficulty', 'medium')
        
        if ai_tutor:
            # Kengaytirilgan quiz
            quiz = ai_tutor.generate_quiz(topic, difficulty, 5)
        else:
            # Oddiy quiz
            quiz = generate_simple_quiz(topic)
        
        return jsonify(quiz)
        
    except Exception as e:
        print(f"❌ Quiz xatolik: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Quiz yaratishda xatolik'
        }), 500

def generate_simple_quiz(topic):
    """Oddiy quiz yaratish"""
    simple_questions = {
        'matematika': [
            {'q': '5 + 3 nechga teng?', 'a': '8', 'options': ['6', '7', '8', '9']},
            {'q': '12 - 4 nechga teng?', 'a': '8', 'options': ['6', '7', '8', '9']},
            {'q': '3 × 4 nechga teng?', 'a': '12', 'options': ['10', '11', '12', '13']}
        ],
        'fizika': [
            {'q': 'Yerning tortish kuchi nechga teng?', 'a': '9.8 m/s²', 'options': ['9.8 m/s²', '10 m/s²', '8 m/s²', '11 m/s²']},
            {'q': 'Yorug\'lik tezligi qancha?', 'a': '300,000 km/s', 'options': ['300,000 km/s', '200,000 km/s', '400,000 km/s', '500,000 km/s']}
        ]
    }
    
    questions = simple_questions.get(topic, simple_questions['matematika'])
    
    quiz_questions = []
    for q_data in questions:
        quiz_questions.append({
            'question': q_data['q'],
            'answer': q_data['a'],
            'options': q_data['options']
        })
    
    return {
        'topic': topic,
        'questions': quiz_questions,
        'total_questions': len(quiz_questions)
    }

@app.route('/api/status')
def status():
    """Tizim holatini tekshirish"""
    return jsonify({
        'ai_model_loaded': ai_tutor is not None,
        'features': {
            'basic_chat': True,
            'enhanced_ai': ai_tutor is not None,
            'web_search': ai_tutor.search_enabled if ai_tutor else False,
            'advanced_quiz': ai_tutor is not None,
            'math_solver': True
        },
        'model_type': 'Enhanced GPT-2' if ai_tutor else 'Basic Fallback'
    })

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Sozlamalarni yangilash"""
    try:
        data = request.get_json()
        
        if ai_tutor and 'web_search' in data:
            ai_tutor.search_enabled = data['web_search']
            
        return jsonify({
            'success': True,
            'message': 'Sozlamalar yangilandi'
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("="*50)
    print("🚀 AI Ta'lim Yordamchisi ishga tushmoqda...")
    print("📱 Brauzerda ochish: http://localhost:5000")
    print("🤖 AI Model:", "✅ Enhanced GPT-2" if ai_tutor else "❌ Basic Mode")
    print("🌐 Web Search:", "✅ Enabled" if ai_tutor and ai_tutor.search_enabled else "❌ Disabled")
    print("📊 Features: Chat, Quiz, Math Solver, Web Search")
    print("="*50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)