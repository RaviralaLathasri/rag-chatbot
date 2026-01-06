// Dynamic API URL based on environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000' 
    : 'https://rag-chatbot-backend.onrender.com'; // Replace with your actual backend URL

let selectedFile = null;
let isProcessing = false;

const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const uploadBtn = document.getElementById('uploadBtn');
const uploadSection = document.getElementById('uploadSection');
const chatContainer = document.getElementById('chatContainer');
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const resetBtn = document.getElementById('resetBtn');
const docName = document.getElementById('docName');
const loadingOverlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        selectedFile = file;
        fileName.textContent = `Selected: ${file.name}`;
        uploadBtn.style.display = 'block';
    }
});

uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    showLoading('Processing your document...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            docName.textContent = `📄 ${data.filename} (${data.chunks} chunks)`;
            uploadSection.style.display = 'none';
            chatContainer.style.display = 'flex';
            showMessage(`Document processed successfully! You can now ask questions about "${data.filename}".`, 'bot');
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert(`Error uploading file: ${error.message}`);
    } finally {
        hideLoading();
    }
});

sendBtn.addEventListener('click', sendMessage);

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

userInput.addEventListener('input', () => {
    userInput.style.height = 'auto';
    userInput.style.height = userInput.scrollHeight + 'px';
});

resetBtn.addEventListener('click', async () => {
    if (confirm('Are you sure you want to upload a new document? Current chat will be cleared.')) {
        try {
            await fetch(`${API_BASE_URL}/reset`, {
                method: 'POST'
            });
            
            selectedFile = null;
            fileName.textContent = '';
            uploadBtn.style.display = 'none';
            fileInput.value = '';
            chatContainer.style.display = 'none';
            uploadSection.style.display = 'block';
            chatMessages.innerHTML = `
                <div class="message bot-message">
                    <div class="message-content">
                        👋 Hello! I'm ready to answer questions about your document. Ask me anything!
                    </div>
                </div>
            `;
        } catch (error) {
            alert(`Error resetting: ${error.message}`);
        }
    }
});

async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message || isProcessing) return;
    
    showMessage(message, 'user');
    userInput.value = '';
    userInput.style.height = 'auto';
    
    isProcessing = true;
    sendBtn.disabled = true;
    
    const thinkingMsg = showMessage('Thinking...', 'bot');
    
    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        thinkingMsg.remove();
        
        if (response.ok) {
            showMessage(data.response, 'bot');
        } else {
            showMessage(`Error: ${data.error}`, 'bot');
        }
    } catch (error) {
        thinkingMsg.remove();
        showMessage(`Error: ${error.message}`, 'bot');
    } finally {
        isProcessing = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function showMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

function showLoading(text) {
    loadingText.textContent = text;
    loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    loadingOverlay.style.display = 'none';
}

async function checkStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/status`);
        if (!response.ok) {
            console.error('Backend not responding');
            return;
        }
        const data = await response.json();
        
        if (data.has_document) {
            docName.textContent = `📄 ${data.filename} (${data.chunks} chunks)`;
            uploadSection.style.display = 'none';
            chatContainer.style.display = 'flex';
        }
    } catch (error) {
        console.error('Error checking status - make sure backend is running:', error);
    }
}

// Check status on page load
checkStatus();
