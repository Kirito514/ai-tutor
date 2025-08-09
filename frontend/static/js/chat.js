let currentUserId = 'user_' + Math.random().toString(36).substr(2, 9);

// Enter tugmasi bosilganda xabar yuborish
document.addEventListener('DOMContentLoaded', function() {
    const messageInput = document.getElementById('messageInput');
    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Fokus input'ga berish
    messageInput.focus();
});

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message) {
        alert('Iltimos, savol yozing!');
        return;
    }
    
    // Send tugmasini vaqtincha o'chirish
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;
    sendBtn.innerHTML = 'Yuborilmoqda...';
    
    // Foydalanuvchi xabarini ko'rsatish
    addMessage(message, 'user');
    input.value = '';
    
    // Loading ko'rsatish
    const loadingId = addMessage('Javob tayyorlanmoqda...', 'bot loading', true);
    
    // Serverga yuborish
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            message: message,
            user_id: currentUserId
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server xatoligi');
        }
        return response.json();
    })
    .then(data => {
        // Loading'ni olib tashlash
        removeMessage(loadingId);
        
        // AI javobini ko'rsatish
        addMessage(data.response, 'bot');
        
        // Suggested topics olib tashlandi
    })
    .catch(error => {
        removeMessage(loadingId);
        addMessage('❌ Xatolik yuz berdi: ' + error.message + '. Qayta urinib ko\'ring.', 'bot error');
    })
    .finally(() => {
        // Send tugmasini qayta yoqish
        sendBtn.disabled = false;
        sendBtn.innerHTML = 'Yuborish';
        input.focus();
    });
}

function addMessage(text, className, isLoading = false) {
    const messages = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    const messageId = 'msg_' + Date.now() + Math.random().toString(36).substr(2, 5);
    
    messageDiv.id = messageId;
    messageDiv.className = `message ${className}`;
    
    if (isLoading) {
        messageDiv.innerHTML = '<div class="loading-dots">Javob tayyorlanmoqda...</div>';
    } else {
        messageDiv.textContent = text;
    }
    
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
    
    return messageId;
}

function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// Ortiqcha funksiyalar olib tashlandi

// Quiz funksiyasi
function requestQuiz(topic = 'matematika') {
    addMessage('Test savollar yaratyapman...', 'bot');
    
    fetch('/api/quiz', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            topic: topic,
            difficulty: 'medium'
        })
    })
    .then(response => response.json())
    .then(data => {
        displayQuiz(data);
    })
    .catch(error => {
        addMessage('Test yaratishda xatolik: ' + error.message, 'bot error');
    });
}

function displayQuiz(quizData) {
    const messages = document.getElementById('messages');
    const quizDiv = document.createElement('div');
    quizDiv.className = 'quiz-container';
    
    let quizHTML = `<h3>📝 ${quizData.topic.toUpperCase()} TEST SAVOLLAR</h3>`;
    
    quizData.questions.forEach((q, index) => {
        quizHTML += `
            <div class="quiz-question">
                <p><strong>${index + 1}. ${q.question}</strong></p>
                <div class="quiz-options">
                    ${q.options.map((option, optIndex) => 
                        `<button class="quiz-option" onclick="selectAnswer(${index}, ${optIndex}, ${q.correct})">
                            ${String.fromCharCode(65 + optIndex)}. ${option}
                        </button>`
                    ).join('')}
                </div>
            </div>
        `;
    });
    
    quizDiv.innerHTML = quizHTML;
    messages.appendChild(quizDiv);
    messages.scrollTop = messages.scrollHeight;
}

function selectAnswer(questionIndex, selectedIndex, correctIndex) {
    const options = document.querySelectorAll(`[onclick*="selectAnswer(${questionIndex}"]`);
    
    options.forEach((option, index) => {
        if (index === correctIndex) {
            option.style.background = '#4CAF50';
            option.style.color = 'white';
            option.innerHTML += ' ✓';
        } else if (index === selectedIndex && selectedIndex !== correctIndex) {
            option.style.background = '#f44336';
            option.style.color = 'white';
            option.innerHTML += ' ✗';
        }
        option.disabled = true;
    });
    
    if (selectedIndex === correctIndex) {
        addMessage('🎉 To\'g\'ri javob!', 'bot');
    } else {
        addMessage('❌ Noto\'g\'ri. To\'g\'ri javob: ' + String.fromCharCode(65 + correctIndex), 'bot');
    }
}