# backend/enhanced_ai_model.py - Yangi kuchli AI model

import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, pipeline
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime

class EnhancedAITutor:
    def __init__(self):
        print("🤖 Kuchli AI yordamchi yuklanmoqda...")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"📱 Qurilma: {self.device}")
        
        # AI modellarni yuklash
        self.load_ai_models()
        
        # Bilimlar bazasi
        self.load_knowledge_base()
        
        # Web search sozlamalari
        self.search_enabled = True
        self.max_search_results = 3
        
    def load_ai_models(self):
        """AI modellarni yuklash"""
        try:
            print("📥 GPT-2 model yuklanmoqda... (biroz vaqt oladi)")
            
            # GPT-2 tokenizer va model
            self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            self.model = GPT2LMHeadModel.from_pretrained('gpt2').to(self.device)
            
            # Padding token qo'shish
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Text generation pipeline
            self.generator = pipeline(
                'text-generation', 
                model=self.model, 
                tokenizer=self.tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            print("✅ GPT-2 model muvaffaqiyatli yuklandi!")
            
        except Exception as e:
            print(f"❌ Model yuklashda xatolik: {e}")
            print("🔄 Oddiy mode'da ishlaymiz...")
            self.generator = None
    
    def load_knowledge_base(self):
        """Kengaytirilgan bilimlar bazasi"""
        self.knowledge_base = {
            # O'zbek tili va adabiyoti
            "o'zbek tili": "O'zbek tili - turkiy tillar oilasiga mansub. 35 million kishi gapiradi.",
            "alisher navoiy": "Alisher Navoiy (1441-1501) - buyuk shoir va davlat arbobi. 'Xamsa' asari mashhur.",
            "abdulla qodiriy": "Abdulla Qodiriy (1894-1938) - o'zbek adabiyotining asoschisi. 'Mehrobdan Chayon' romani.",
            
            # Matematika
            "integral": "Integral - funksiya ostidagi yuzani hisoblash. ∫f(x)dx ko'rinishda yoziladi.",
            "limit": "Limit - x ma'lum qiymatga yaqinlashgandagi funksiya qiymati. lim x→a f(x)",
            "differensial": "Differensial - funksiyaning o'zgarish tezligi. f'(x) yoki dy/dx bilan belgilanadi.",
            "matrisa": "Matrisa - sonlarning to'rtburchak jadval ko'rinishidagi joylashishi.",
            
            # Fizika
            "nisbiylik nazariyasi": "Einstein nazariyasi: E=mc², vaqt va fazo nisbiy.",
            "kvant fizika": "Kvant mexanikasi - atom va subatom zarrachalar harakati qonunlari.",
            "termodinamika": "Termodinamika - issiqlik va energiya o'zgarishi qonunlari.",
            "elektromagnetizm": "Elektr va magnit maydonlarning o'zaro ta'siri.",
            
            # Kimyo
            "organik kimyo": "Organik kimyo - uglerod tutgan birikmalarni o'rganadi.",
            "noorganik kimyo": "Noorganik kimyo - uglerod tutmagan elementlar va birikmalar.",
            "fizik kimyo": "Fizik kimyo - kimyoviy hodisalarning fizik asoslarini o'rganadi.",
            "analitik kimyo": "Analitik kimyo - moddalar tarkibini aniqlash usullari.",
            
            # Biologiya
            "genetika": "Genetika - irsiyat qonunlarini o'rganuvchi fan. DNA, RNK.",
            "evolyutsiya": "Evolyutsiya - tirik mavjudotlarning vaqt davomida o'zgarishi.",
            "ekologiya": "Ekologiya - organizmlar va atrof-muhit munosabatlari.",
            "mikrobiologiya": "Mikrobiologiya - ko'zga ko'rinmas organizmlarni o'rganish.",
            
            # Tarix
            "ipak yo'li": "Ipak yo'li - Sharq va G'arbni bog'lagan savdo yo'li. Samarqand, Buxoro muhim nuqtalar.",
            "movarounahr": "Movarounahr - Amudaryo va Sirdaryo orasidagi hudud. O'zbekiston markazi.",
            "timurid davlati": "Temuriylar (1370-1507) - O'rta Osiyoda kuchli imperiya.",
            
            # Zamonaviy mavzular
            "sun'iy intellekt": "AI - kompyuterlarni inson kabi o'ylashga o'rgatish texnologiyasi.",
            "blockchain": "Blockchain - ma'lumotlarni himoya qiluvchi zanjir texnologiyasi.",
            "python dasturlash": "Python - oddiy va kuchli dasturlash tili. AI uchun eng mashhur.",
            
            # Iqtisod
            "bozor iqtisodiyoti": "Bozor iqtisodiyoti - talab va taklif asosida narx shakllanishi.",
            "inflyatsiya": "Inflyatsiya - tovarlar narxining umumiy o'sishi.",
            "valyuta": "Valyuta - xalqaro to'lov vositasi. Dollar, yevro, so'm.",
        }
    
    def generate_response(self, user_message, user_id=None):
        """Foydalanuvchi savoliga javob yaratish"""
        
        # 1. Bilimlar bazasidan qidirish
        kb_response = self.search_knowledge_base(user_message)
        if kb_response:
            return self.enhance_with_ai(kb_response, user_message)
        
        # 2. Matematika masalasi ekanligini tekshirish
        if self.is_math_problem(user_message):
            return self.solve_math(user_message)
        
        # 3. Web'dan qidirish (agar ruxsat berilsa)
        if self.search_enabled and self.should_search_web(user_message):
            web_info = self.search_web(user_message)
            if web_info:
                return self.create_response_with_web_data(user_message, web_info)
        
        # 4. AI model bilan javob yaratish
        if self.generator:
            return self.generate_ai_response(user_message)
        
        # 5. Default javob
        return self.generate_default_response(user_message)
    
    def search_knowledge_base(self, query):
        """Bilimlar bazasida qidirish"""
        query_lower = query.lower()
        
        # To'liq mos kelish
        if query_lower in self.knowledge_base:
            return self.knowledge_base[query_lower]
        
        # Kalit so'zlar bo'yicha qidirish
        for key, value in self.knowledge_base.items():
            if key in query_lower or any(word in query_lower for word in key.split()):
                return value
        
        return None
    
    def enhance_with_ai(self, base_response, user_question):
        """Asosiy javobni AI bilan boyitish"""
        # GPT-2 model O'zbek tilida yaxshi ishlamagani uchun
        # faqat asosiy javobni qaytaramiz
        return base_response
    
    def is_math_problem(self, text):
        """Matematika masalasi ekanligini aniqlash"""
        math_patterns = [
            r'\d+\s*[\+\-\*/]\s*\d+',  # 2+2, 5*3
            r'x\s*[\+\-\*/=]\s*\d+',   # x+5=10
            r'sin|cos|tan|log',         # trigonometriya
            r'integral|differensial|limit',  # matematika terminlari
            r'tenglama|funksiya|grafik'
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, text.lower()):
                return True
        return False
    
    def solve_math(self, problem):
        """Matematik masalani yechish"""
        problem_lower = problem.lower()
        
        # Oddiy amallar
        if '+' in problem:
            try:
                # Xavfsiz eval uchun
                numbers = re.findall(r'\d+', problem)
                if len(numbers) >= 2:
                    result = sum(int(n) for n in numbers)
                    return f"Javob: {' + '.join(numbers)} = {result}"
            except:
                pass
        
        if '-' in problem:
            try:
                numbers = re.findall(r'\d+', problem)
                if len(numbers) >= 2:
                    result = int(numbers[0]) - int(numbers[1])
                    return f"Javob: {numbers[0]} - {numbers[1]} = {result}"
            except:
                pass
        
        if '*' in problem or 'x' in problem.replace('x=', ''):
            try:
                numbers = re.findall(r'\d+', problem)
                if len(numbers) >= 2:
                    result = int(numbers[0]) * int(numbers[1])
                    return f"Javob: {numbers[0]} × {numbers[1]} = {result}"
            except:
                pass
        
        return "Bu matematik masalani yecha olmadim. Boshqa ko'rinishda yozib ko'ring."
    
    def should_search_web(self, query):
        """Web'da qidirish kerakligini aniqlash"""
        current_keywords = ['yangi', 'hozir', 'bugun', '2024', '2025', 'so\'nggi', 'eng yangi']
        news_keywords = ['yangiliklar', 'xabarlar', 'hodisa', 'voqea']
        
        query_lower = query.lower()
        
        return any(keyword in query_lower for keyword in current_keywords + news_keywords)
    
    def search_web(self, query):
        """Web'dan qidirish"""
        try:
            # Google qidirish URL
            search_url = f"https://www.google.com/search?q={query}&hl=uz"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Qidiruv natijalarini olish
                results = []
                for div in soup.find_all('div', class_='BVG0Nb')[:self.max_search_results]:
                    text = div.get_text()
                    if len(text) > 50:
                        results.append(text[:200] + "...")
                
                return results
                
        except Exception as e:
            print(f"Web search xatolik: {e}")
            
        return None
    
    def create_response_with_web_data(self, query, web_results):
        """Web ma'lumotlari bilan javob yaratish"""
        response = f"🌐 '{query}' bo'yicha topilgan ma'lumotlar:\n\n"
        
        for i, result in enumerate(web_results, 1):
            response += f"{i}. {result}\n\n"
        
        response += "ℹ️ Bu ma'lumotlar internet'dan olingan. Aniqlik uchun rasmiy manbalarni tekshiring."
        
        return response
    
    def generate_ai_response(self, user_message):
        """AI model bilan javob yaratish"""
        try:
            # O'zbek tilida oddiy prompt
            prompt = f"Question: {user_message}\nAnswer:"
            
            response = self.generator(
                prompt,
                max_new_tokens=50,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                truncation=True,
                clean_up_tokenization_spaces=True
            )
            
            generated = response[0]['generated_text']
            answer = generated[len(prompt):].strip()
            
            # Noto'g'ri javoblarni filtrlash
            if answer and len(answer) > 5 and not self.is_gibberish(answer):
                return f"🤖 {answer}"
            
        except Exception as e:
            print(f"AI response xatolik: {e}")
        
        return self.generate_default_response(user_message)
    
    def is_gibberish(self, text):
        """Noto'g'ri javoblarni aniqlash"""
        gibberish_patterns = [
            'nibik', 'babad', 'kevlar', 'kovlar', 'karunu', 'tzemat', 'kara'
        ]
        
        text_lower = text.lower()
        for pattern in gibberish_patterns:
            if pattern in text_lower:
                return True
        
        # Takrorlanuvchi so'zlarni tekshirish
        words = text.split()
        if len(words) > 3 and len(set(words)) < len(words) / 2:
            return True
            
        return False
    
    def generate_default_response(self, user_message):
        """Default javob"""
        message_lower = user_message.lower()
        
        # Maxsus savollar uchun javoblar
        if 'nima qila olasan' in message_lower or 'qila olasan' in message_lower:
            return """Men quyidagi ishlarni qila olaman:

📚 **Ta'lim sohasida:**
• Matematika masalalarini yechish
• Fizika, kimyo qonunlarini tushuntirish  
• Tarix voqealarini bayon qilish
• O'zbek tili va adabiyoti bo'yicha ma'lumot

🧮 **Matematik amallar:**
• Oddiy hisob-kitoblar (2+2, 5*3)
• Tenglama yechish
• Geometriya masalalari

📝 **Test yaratish:**
• Turli fanlar bo'yicha test savollar
• Javoblar bilan birga

🌐 **Qidiruv:**
• Yangi ma'lumotlar topish
• So'nggi yangiliklar

Qanday yordam kerak?"""
        
        # Boshqa umumiy javoblar
        responses = [
            "Bu mavzu bo'yicha aniqroq savol bering.",
            "Bu haqda batafsil ma'lumot kerak. Qaysi jihatini bilmoqchisiz?",
            "Savolni boshqacha qilib so'rab ko'ring.",
            "Bu mavzuda yordam bera olaman. Aniqroq tushuntiring."
        ]
        
        import random
        return random.choice(responses)
    
    def generate_quiz(self, topic, difficulty='medium', num_questions=5):
        """Test savollar yaratish"""
        
        # Mavzu bo'yicha savollar bazasi
        quiz_templates = {
            'matematika': [
                {'q': 'Kvadrat ildizi {} ning qiymati nechaga teng?', 'type': 'sqrt'},
                {'q': 'Agar x + {} = {}, x ning qiymati necha?', 'type': 'equation'},
                {'q': '{} × {} ning natijasi?', 'type': 'multiply'},
                {'q': 'Uchburchakning barcha burchaklari yig\'indisi nechaga teng?', 'answer': '180°'},
                {'q': 'Pi soni taxminan qanchaga teng?', 'answer': '3.14159'}
            ],
            'fizika': [
                {'q': 'Yerning tortishish tezlanishi nechaga teng?', 'answer': '9.8 m/s²'},
                {'q': 'Yorug\'lik tezligi qancha?', 'answer': '300,000 km/s'},
                {'q': 'Energiya saqlanish qonuni nima deydi?', 'answer': 'Energiya yo\'qolmaydi, faqat shaklini o\'zgartiradi'},
                {'q': 'Elektr qarshilik birligi nima?', 'answer': 'Om (Ω)'},
                {'q': 'Atmosfera bosimi nechaga teng?', 'answer': '101,325 Pa'}
            ],
            'kimyo': [
                {'q': 'Suvning kimyoviy formulasi?', 'answer': 'H₂O'},
                {'q': 'Kislorodning kimyoviy belgisi?', 'answer': 'O'},
                {'q': 'Tuzning kimyoviy nomi?', 'answer': 'Natriy xlorid (NaCl)'},
                {'q': 'Uglerodni oksidning formulasi?', 'answer': 'CO₂'},
                {'q': 'pH shkalasi qancha oraliqda?', 'answer': '0 dan 14 gacha'}
            ]
        }
        
        if topic.lower() not in quiz_templates:
            topic = 'matematika'
        
        questions = []
        templates = quiz_templates[topic.lower()]
        
        import random
        selected_templates = random.sample(templates, min(num_questions, len(templates)))
        
        for template in selected_templates:
            if template['type'] == 'sqrt' if 'type' in template else False:
                num = random.choice([4, 9, 16, 25, 36, 49, 64, 81, 100])
                questions.append({
                    'question': template['q'].format(num),
                    'answer': str(int(num ** 0.5)),
                    'options': self.generate_options(str(int(num ** 0.5)), 'number')
                })
            elif template.get('type') == 'equation':
                a = random.randint(1, 10)
                b = random.randint(11, 20)
                answer = b - a
                questions.append({
                    'question': template['q'].format(a, b),
                    'answer': str(answer),
                    'options': self.generate_options(str(answer), 'number')
                })
            elif template.get('type') == 'multiply':
                a = random.randint(2, 12)
                b = random.randint(2, 12)
                answer = a * b
                questions.append({
                    'question': template['q'].format(a, b),
                    'answer': str(answer),
                    'options': self.generate_options(str(answer), 'number')
                })
            else:
                questions.append({
                    'question': template['q'],
                    'answer': template['answer'],
                    'options': self.generate_options(template['answer'], 'text')
                })
        
        return {
            'topic': topic,
            'difficulty': difficulty,
            'questions': questions,
            'total_questions': len(questions)
        }
    
    def generate_options(self, correct_answer, answer_type):
        """Test variantlari yaratish"""
        if answer_type == 'number':
            correct = int(correct_answer)
            options = [correct]
            
            # Noto'g'ri variantlar
            while len(options) < 4:
                wrong = correct + random.randint(-10, 10)
                if wrong != correct and wrong not in options and wrong > 0:
                    options.append(wrong)
            
            random.shuffle(options)
            return [str(opt) for opt in options]
        
        else:  # text
            # Oddiy text uchun standard variantlar
            options = [correct_answer, "Noto'g'ri variant 1", "Noto'g'ri variant 2", "Noto'g'ri variant 3"]
            random.shuffle(options)
            return options