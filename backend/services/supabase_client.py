from supabase import create_client, Client
from config import Config
import bcrypt
import uuid
from datetime import datetime, timedelta
import secrets

class SupabaseService:
    def __init__(self):
        self.client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        self.service_client: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_KEY)
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    # User operations
    def create_user(self, username: str, email: str, first_name: str, 
                   last_name: str, other_name: str, password: str) -> dict:
        """Create a new user"""
        try:
            password_hash = self.hash_password(password)
            
            response = self.service_client.table('users').insert({
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'other_name': other_name,
                'password_hash': password_hash
            }).execute()
            
            return {'success': True, 'data': response.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_by_username(self, username: str) -> dict:
        """Get user by username"""
        try:
            response = self.service_client.table('users').select('*').eq('username', username).execute()
            if response.data:
                return {'success': True, 'data': response.data[0]}
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_by_email(self, email: str) -> dict:
        """Get user by email"""
        try:
            response = self.service_client.table('users').select('*').eq('email', email).execute()
            if response.data:
                return {'success': True, 'data': response.data[0]}
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_by_id(self, user_id: str) -> dict:
        """Get user by ID"""
        try:
            response = self.service_client.table('users').select('*').eq('id', user_id).execute()
            if response.data:
                return {'success': True, 'data': response.data[0]}
            return {'success': False, 'error': 'User not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_user_password(self, user_id: str, new_password: str) -> dict:
        """Update user password"""
        try:
            password_hash = self.hash_password(new_password)
            response = self.service_client.table('users').update({
                'password_hash': password_hash
            }).eq('id', user_id).execute()
            
            return {'success': True, 'data': response.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_user(self, user_id: str) -> dict:
        """Delete user account"""
        try:
            response = self.service_client.table('users').delete().eq('id', user_id).execute()
            return {'success': True, 'data': response.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Chat operations
    def create_chat(self, user_id: str, title: str) -> dict:
        """Create a new chat"""
        try:
            response = self.service_client.table('chats').insert({
                'user_id': user_id,
                'title': title
            }).execute()
            
            return {'success': True, 'data': response.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_chats(self, user_id: str) -> dict:
        """Get all chats for a user"""
        try:
            response = self.service_client.table('chats').select('*').eq('user_id', user_id).eq('is_active', True).order('updated_at', desc=True).execute()
            return {'success': True, 'data': response.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_chat_by_id(self, chat_id: str, user_id: str) -> dict:
        """Get a specific chat by ID"""
        try:
            response = self.service_client.table('chats').select('*').eq('id', chat_id).eq('user_id', user_id).execute()
            if response.data:
                return {'success': True, 'data': response.data[0]}
            return {'success': False, 'error': 'Chat not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_chat_title(self, chat_id: str, title: str, user_id: str) -> dict:
        """Update chat title"""
        try:
            response = self.service_client.table('chats').update({
                'title': title
            }).eq('id', chat_id).eq('user_id', user_id).execute()
            
            return {'success': True, 'data': response.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_chat(self, chat_id: str, user_id: str) -> dict:
        """Delete a chat"""
        try:
            response = self.service_client.table('chats').update({
                'is_active': False
            }).eq('id', chat_id).eq('user_id', user_id).execute()
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Message operations
    def create_message(self, chat_id: str, content: str, role: str, message_order: int) -> dict:
        """Create a new message"""
        try:
            response = self.service_client.table('messages').insert({
                'chat_id': chat_id,
                'content': content,
                'role': role,
                'message_order': message_order
            }).execute()
            
            return {'success': True, 'data': response.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_chat_messages(self, chat_id: str, user_id: str) -> dict:
        """Get all messages for a chat"""
        try:
            # First verify the chat belongs to the user
            chat_result = self.get_chat_by_id(chat_id, user_id)
            if not chat_result['success']:
                return chat_result
            
            response = self.service_client.table('messages').select('*').eq('chat_id', chat_id).order('message_order').execute()
            return {'success': True, 'data': response.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_last_message_order(self, chat_id: str) -> int:
        """Get the last message order for a chat"""
        try:
            response = self.service_client.table('messages').select('message_order').eq('chat_id', chat_id).order('message_order', desc=True).limit(1).execute()
            if response.data:
                return response.data[0]['message_order']
            return 0
        except Exception as e:
            return 0
    
    # File operations
    def create_file_record(self, chat_id: str, user_id: str, filename: str, 
                          file_type: str, file_size: int, file_path: str, 
                          supabase_storage_path: str = None) -> dict:
        """Create a file record"""
        try:
            response = self.service_client.table('files').insert({
                'chat_id': chat_id,
                'user_id': user_id,
                'filename': filename,
                'file_type': file_type,
                'file_size': file_size,
                'file_path': file_path,
                'supabase_storage_path': supabase_storage_path
            }).execute()
            
            return {'success': True, 'data': response.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_chat_files(self, chat_id: str, user_id: str) -> dict:
        """Get all files for a chat"""
        try:
            response = self.service_client.table('files').select('*').eq('chat_id', chat_id).eq('user_id', user_id).order('created_at', desc=True).execute()
            return {'success': True, 'data': response.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def delete_file_record(self, file_id: str, user_id: str) -> dict:
        """Delete a file record"""
        try:
            response = self.service_client.table('files').delete().eq('id', file_id).eq('user_id', user_id).execute()
            return {'success': True, 'data': response.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_file_processed_content(self, file_id: str, content: str) -> dict:
        """Update file processed content"""
        try:
            response = self.service_client.table('files').update({
                'processed_content': content,
                'is_processed': True
            }).eq('id', file_id).execute()
            
            return {'success': True, 'data': response.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Password reset operations
    def create_password_reset_token(self, user_id: str) -> dict:
        """Create a password reset token"""
        try:
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=1)
            
            response = self.service_client.table('password_reset_tokens').insert({
                'user_id': user_id,
                'token': token,
                'expires_at': expires_at.isoformat()
            }).execute()
            
            return {'success': True, 'data': response.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def verify_password_reset_token(self, token: str) -> dict:
        """Verify a password reset token"""
        try:
            response = self.service_client.table('password_reset_tokens').select('*').eq('token', token).eq('used', False).execute()
            
            if not response.data:
                return {'success': False, 'error': 'Invalid token'}
            
            token_data = response.data[0]
            expires_at = datetime.fromisoformat(token_data['expires_at'].replace('Z', '+00:00'))
            
            if datetime.utcnow() > expires_at.replace(tzinfo=None):
                return {'success': False, 'error': 'Token expired'}
            
            return {'success': True, 'data': token_data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def mark_password_reset_token_used(self, token: str) -> dict:
        """Mark a password reset token as used"""
        try:
            response = self.service_client.table('password_reset_tokens').update({
                'used': True
            }).eq('token', token).execute()
            
            return {'success': True, 'data': response.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global instance
supabase_service = SupabaseService()
