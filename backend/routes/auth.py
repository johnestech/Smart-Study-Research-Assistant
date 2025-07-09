from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from services import supabase_service
import re
import validators

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    return validators.email(email)

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\\d", password):
        return False, "Password must contain at least one number"
    
    return True, "Password is valid"

def validate_username(username):
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if len(username) > 50:
        return False, "Username must be no more than 50 characters long"
    
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, "Username is valid"

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Required fields
        required_fields = ['username', 'email', 'first_name', 'last_name', 'password', 'confirm_password']
        for field in required_fields:
            if field not in data or not data[field].strip():
                return jsonify({'error': f'{field} is required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip().lower()
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        other_name = data.get('other_name', '').strip()
        password = data['password']
        confirm_password = data['confirm_password']
        
        # Validate input
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        username_valid, username_msg = validate_username(username)
        if not username_valid:
            return jsonify({'error': username_msg}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        password_valid, password_msg = validate_password(password)
        if not password_valid:
            return jsonify({'error': password_msg}), 400
        
        # Check if username already exists
        existing_user = supabase_service.get_user_by_username(username)
        if existing_user['success']:
            return jsonify({'error': 'Username already exists'}), 409
        
        # Check if email already exists
        existing_email = supabase_service.get_user_by_email(email)
        if existing_email['success']:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Create user
        result = supabase_service.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            other_name=other_name,
            password=password
        )
        
        if result['success']:
            user_data = result['data']
            # Create access token
            access_token = create_access_token(identity=user_data['id'])
            
            return jsonify({
                'message': 'User created successfully',
                'user': {
                    'id': user_data['id'],
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'other_name': user_data['other_name']
                },
                'access_token': access_token
            }), 201
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        # Required fields
        if 'login' not in data or 'password' not in data:
            return jsonify({'error': 'Login (username/email) and password are required'}), 400
        
        login_value = data['login'].strip()
        password = data['password']
        
        # Determine if login is email or username
        user_result = None
        if validate_email(login_value):
            user_result = supabase_service.get_user_by_email(login_value.lower())
        else:
            user_result = supabase_service.get_user_by_username(login_value)
        
        if not user_result['success']:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user_data = user_result['data']
        
        # Verify password
        if not supabase_service.verify_password(password, user_data['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if not user_data.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user_data['id'])
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'other_name': user_data['other_name'],
                'profile_photo_url': user_data.get('profile_photo_url')
            },
            'access_token': access_token
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        
        result = supabase_service.get_user_by_id(user_id)
        if not result['success']:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = result['data']
        return jsonify({
            'user': {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'other_name': user_data['other_name'],
                'profile_photo_url': user_data.get('profile_photo_url'),
                'created_at': user_data['created_at']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'current_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Get user data
        user_result = supabase_service.get_user_by_id(user_id)
        if not user_result['success']:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_result['data']
        
        # Verify current password
        if not supabase_service.verify_password(current_password, user_data['password_hash']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Validate new password
        password_valid, password_msg = validate_password(new_password)
        if not password_valid:
            return jsonify({'error': password_msg}), 400
        
        # Update password
        result = supabase_service.update_user_password(user_id, new_password)
        if result['success']:
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].strip().lower()
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user exists
        user_result = supabase_service.get_user_by_email(email)
        if not user_result['success']:
            # Don't reveal if email exists or not for security
            return jsonify({'message': 'If the email exists, a password reset link has been sent'}), 200
        
        user_data = user_result['data']
        
        # Create password reset token
        token_result = supabase_service.create_password_reset_token(user_data['id'])
        if token_result['success']:
            # In a real application, you would send an email here
            # For now, we'll just return success
            return jsonify({'message': 'Password reset link has been sent to your email'}), 200
        else:
            return jsonify({'error': 'Failed to generate reset token'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        
        required_fields = ['token', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        token = data['token']
        new_password = data['new_password']
        
        # Validate new password
        password_valid, password_msg = validate_password(new_password)
        if not password_valid:
            return jsonify({'error': password_msg}), 400
        
        # Verify token
        token_result = supabase_service.verify_password_reset_token(token)
        if not token_result['success']:
            return jsonify({'error': token_result['error']}), 400
        
        token_data = token_result['data']
        user_id = token_data['user_id']
        
        # Update password
        password_result = supabase_service.update_user_password(user_id, new_password)
        if not password_result['success']:
            return jsonify({'error': password_result['error']}), 500
        
        # Mark token as used
        supabase_service.mark_password_reset_token_used(token)
        
        return jsonify({'message': 'Password reset successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    """Delete user account"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'password' not in data:
            return jsonify({'error': 'Password confirmation is required'}), 400
        
        password = data['password']
        
        # Get user data
        user_result = supabase_service.get_user_by_id(user_id)
        if not user_result['success']:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user_result['data']
        
        # Verify password
        if not supabase_service.verify_password(password, user_data['password_hash']):
            return jsonify({'error': 'Password is incorrect'}), 401
        
        # Delete user account
        result = supabase_service.delete_user(user_id)
        if result['success']:
            return jsonify({'message': 'Account deleted successfully'}), 200
        else:
            return jsonify({'error': result['error']}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
