from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services import supabase_service, gemini_service, file_processor
import uuid
from werkzeug.utils import secure_filename
import os

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chats', methods=['GET'])
@jwt_required()
def get_user_chats():
    """Get all chats for the current user"""
    try:
        user_id = get_jwt_identity()
        
        result = supabase_service.get_user_chats(user_id)
        if result['success']:
            return jsonify({'chats': result['data']}), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chats', methods=['POST'])
@jwt_required()
def create_chat():
    """Create a new chat"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Generate title or use provided title
        title = data.get('title', 'New Chat')
        if 'first_message' in data:
            title = gemini_service.generate_chat_title(data['first_message'])
        
        result = supabase_service.create_chat(user_id, title)
        if result['success']:
            return jsonify({'chat': result['data']}), 201
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chats/<chat_id>', methods=['GET'])
@jwt_required()
def get_chat():
    """Get a specific chat with its messages"""
    try:
        user_id = get_jwt_identity()
        chat_id = request.view_args['chat_id']
        
        # Get chat info
        chat_result = supabase_service.get_chat_by_id(chat_id, user_id)
        if not chat_result['success']:
            return jsonify({'error': 'Chat not found'}), 404
        
        # Get messages
        messages_result = supabase_service.get_chat_messages(chat_id, user_id)
        if not messages_result['success']:
            return jsonify({'error': messages_result['error']}), 500
        
        # Get files
        files_result = supabase_service.get_chat_files(chat_id, user_id)
        files = files_result['data'] if files_result['success'] else []
        
        return jsonify({
            'chat': chat_result['data'],
            'messages': messages_result['data'],
            'files': files
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chats/<chat_id>', methods=['PUT'])
@jwt_required()
def update_chat():
    """Update chat title"""
    try:
        user_id = get_jwt_identity()
        chat_id = request.view_args['chat_id']
        data = request.get_json()
        
        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        title = data['title'].strip()
        if not title:
            return jsonify({'error': 'Title cannot be empty'}), 400
        
        result = supabase_service.update_chat_title(chat_id, title, user_id)
        if result['success']:
            return jsonify({'chat': result['data']}), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chats/<chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat():
    """Delete a chat"""
    try:
        user_id = get_jwt_identity()
        chat_id = request.view_args['chat_id']
        
        result = supabase_service.delete_chat(chat_id, user_id)
        if result['success']:
            return jsonify({'message': 'Chat deleted successfully'}), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chats/<chat_id>/messages', methods=['POST'])
@jwt_required()
def send_message():
    """Send a message and get AI response"""
    try:
        user_id = get_jwt_identity()
        chat_id = request.view_args['chat_id']
        data = request.get_json()
        
        if 'content' not in data:
            return jsonify({'error': 'Message content is required'}), 400
        
        content = data['content'].strip()
        if not content:
            return jsonify({'error': 'Message content cannot be empty'}), 400
        
        # Verify chat belongs to user
        chat_result = supabase_service.get_chat_by_id(chat_id, user_id)
        if not chat_result['success']:
            return jsonify({'error': 'Chat not found'}), 404
        
        # Get current message order
        last_order = supabase_service.get_last_message_order(chat_id)
        user_message_order = last_order + 1
        assistant_message_order = last_order + 2
        
        # Save user message
        user_message_result = supabase_service.create_message(
            chat_id, content, 'user', user_message_order
        )
        
        if not user_message_result['success']:
            return jsonify({'error': 'Failed to save user message'}), 500
        
        # Get chat history for context
        messages_result = supabase_service.get_chat_messages(chat_id, user_id)
        chat_history = messages_result['data'] if messages_result['success'] else []
        
        # Get file contents for context
        files_result = supabase_service.get_chat_files(chat_id, user_id)
        document_contents = []
        
        if files_result['success']:
            for file_record in files_result['data']:
                if file_record.get('processed_content'):
                    document_contents.append(file_record['processed_content'])
        
        # Generate AI response
        ai_response = gemini_service.generate_response(
            question=content,
            document_contents=document_contents,
            chat_history=chat_history[:-1]  # Exclude the current message
        )
        
        if not ai_response['success']:
            return jsonify({'error': ai_response['error']}), 500
        
        # Save assistant message
        assistant_message_result = supabase_service.create_message(
            chat_id, ai_response['response'], 'assistant', assistant_message_order
        )
        
        if not assistant_message_result['success']:
            return jsonify({'error': 'Failed to save assistant message'}), 500
        
        # Update chat title if this is the first message
        if user_message_order == 1:
            new_title = gemini_service.generate_chat_title(content)
            supabase_service.update_chat_title(chat_id, new_title, user_id)
        
        return jsonify({
            'user_message': user_message_result['data'],
            'assistant_message': assistant_message_result['data']
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chats/<chat_id>/files', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file to a chat"""
    try:
        user_id = get_jwt_identity()
        chat_id = request.view_args['chat_id']
        
        # Verify chat belongs to user
        chat_result = supabase_service.get_chat_by_id(chat_id, user_id)
        if not chat_result['success']:
            return jsonify({'error': 'Chat not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read file data
        file_data = file.read()
        filename = secure_filename(file.filename)
        
        # Validate file
        validation_result = file_processor.validate_file(file_data, filename)
        if not validation_result['valid']:
            return jsonify({'error': validation_result['error']}), 400
        
        # Get file info
        file_info = file_processor.get_file_info(file_data, filename)
        
        # Extract content
        content_result = file_processor.extract_content(file_data, filename)
        
        # Create file record
        file_record_result = supabase_service.create_file_record(
            chat_id=chat_id,
            user_id=user_id,
            filename=filename,
            file_type=file_info['file_type'],
            file_size=file_info['file_size'],
            file_path=f"uploads/{user_id}/{chat_id}/{filename}"
        )
        
        if not file_record_result['success']:
            return jsonify({'error': 'Failed to create file record'}), 500
        
        file_record = file_record_result['data']
        
        # Update with processed content if extraction was successful
        if content_result['success']:
            supabase_service.update_file_processed_content(
                file_record['id'], 
                content_result['content']
            )
            file_record['processed_content'] = content_result['content']
            file_record['is_processed'] = True
        
        # Create a preview for the response
        preview = ""
        if content_result['success']:
            preview = file_processor.create_file_preview(content_result['content'])
        
        return jsonify({
            'file': file_record,
            'preview': preview,
            'extraction_success': content_result['success'],
            'extraction_error': content_result.get('error')
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chats/<chat_id>/files', methods=['GET'])
@jwt_required()
def get_chat_files():
    """Get all files for a chat"""
    try:
        user_id = get_jwt_identity()
        chat_id = request.view_args['chat_id']
        
        # Verify chat belongs to user
        chat_result = supabase_service.get_chat_by_id(chat_id, user_id)
        if not chat_result['success']:
            return jsonify({'error': 'Chat not found'}), 404
        
        result = supabase_service.get_chat_files(chat_id, user_id)
        if result['success']:
            return jsonify({'files': result['data']}), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/files/<file_id>', methods=['DELETE'])
@jwt_required()
def delete_file():
    """Delete a file"""
    try:
        user_id = get_jwt_identity()
        file_id = request.view_args['file_id']
        
        result = supabase_service.delete_file_record(file_id, user_id)
        if result['success']:
            return jsonify({'message': 'File deleted successfully'}), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
