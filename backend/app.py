from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from document_processor import DocumentProcessor
from rag_engine import RAGEngine

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
KNOWLEDGE_BASE_FOLDER = 'knowledge_base'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KNOWLEDGE_BASE_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

doc_processor = DocumentProcessor()
rag_engine = RAGEngine()

current_knowledge_base = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/upload', methods=['POST'])
def upload_file():
    global current_knowledge_base
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only PDF and TXT allowed'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        text = doc_processor.extract_text(filepath)
        
        if not text or len(text.strip()) < 10:
            os.remove(filepath)
            return jsonify({'error': 'Could not extract text from file or file is too short'}), 400
        
        chunks = doc_processor.chunk_text(text)
        
        knowledge_base = {
            'filename': filename,
            'total_chunks': len(chunks),
            'chunks': chunks
        }
        
        kb_filename = f"{filename.rsplit('.', 1)[0]}_kb.json"
        kb_filepath = os.path.join(KNOWLEDGE_BASE_FOLDER, kb_filename)
        
        with open(kb_filepath, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
        
        current_knowledge_base = knowledge_base
        
        os.remove(filepath)
        
        return jsonify({
            'message': 'File processed successfully',
            'filename': filename,
            'chunks': len(chunks),
            'preview': text[:200] + '...' if len(text) > 200 else text
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    global current_knowledge_base
    
    if current_knowledge_base is None:
        return jsonify({'error': 'No document uploaded. Please upload a document first.'}), 400
    
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400
    
    user_message = data['message']
    
    if not user_message.strip():
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    try:
        response = rag_engine.generate_response(user_message, current_knowledge_base)
        
        return jsonify({
            'response': response,
            'source': current_knowledge_base['filename']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error generating response: {str(e)}'}), 500

@app.route('/reset', methods=['POST'])
def reset():
    global current_knowledge_base
    current_knowledge_base = None
    
    return jsonify({'message': 'Knowledge base reset successfully'}), 200

@app.route('/status', methods=['GET'])
def status():
    global current_knowledge_base
    
    if current_knowledge_base:
        return jsonify({
            'has_document': True,
            'filename': current_knowledge_base['filename'],
            'chunks': current_knowledge_base['total_chunks']
        }), 200
    else:
        return jsonify({
            'has_document': False
        }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
