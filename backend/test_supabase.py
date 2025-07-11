from services import supabase_service

def test_connection():
    # print("Testing get_user_by_username...")
    # result = supabase_service.get_user_by_username('testuser')
    # print("Result:", result)

    print("Testing get_user_by_email...")
    result = supabase_service.get_user_by_email('ebugajohn5646@gmail.com')
    print("Result:", result)

    print("creating user...")
    result = supabase_service.create_user(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        other_name='',
        password='Testpassword123'
    )
    print("Result:", result)

def test_password_verification():
    print("Testing password verification...")
    user = supabase_service.get_user_by_username('testuser')
    if user['success']:
        password_hash = user['data']['password_hash']
        print("Verifying correct password:", supabase_service.verify_password('Testpassword123', password_hash))
        print("Verifying wrong password:", supabase_service.verify_password('wrongpassword', password_hash))
    else:
        print("User not found for password verification.")


if __name__ == '__main__':
    test_connection()
    test_password_verification()