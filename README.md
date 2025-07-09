# Smart Study and Research Assistant

A full-stack web application that leverages the Gemini 2.0 Flash model for academic Q&A based on user-uploaded documents.

## Features

- **Document Support**: PDF, Word (.doc, .docx), PowerPoint (.ppt, .pptx), and image files (.jpg, .jpeg, .png, .gif)
- **AI-Powered Q&A**: Using Gemini 2.0 Flash model for academic research assistance
- **Persistent Chat History**: Maintain conversations across sessions
- **User Authentication**: Secure login/signup with Supabase
- **Responsive Design**: Optimized for both mobile and desktop
- **File Management**: Upload, preview, and manage documents in chat

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: React
- **Database & Auth**: Supabase
- **AI Model**: Google Gemini 2.0 Flash

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Supabase account

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd study-research-assistant
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Environment Configuration

Create `.env` files in both backend and frontend directories:

#### Backend `.env`:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
GOOGLE_API_KEY=your_google_gemini_api_key
FLASK_SECRET_KEY=your_flask_secret_key
FLASK_ENV=development
```

#### Frontend `.env`:
```
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
REACT_APP_API_BASE_URL=http://localhost:5000
```

### 5. Supabase Setup

1. Create a new Supabase project
2. Run the SQL schema provided in `backend/database/schema.sql`
3. Configure authentication settings
4. Set up storage bucket for file uploads

### 6. Running the Application

#### Start Backend:
```bash
cd backend
python app.py
```

#### Start Frontend:
```bash
cd frontend
npm start
```

The application will be available at `http://localhost:3000`

## Project Structure

```
study-research-assistant/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── database/
│   │   └── schema.sql
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── chat.py
│   │   └── message.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── chat.py
│   │   └── ai.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── supabase_client.py
│   │   ├── gemini_client.py
│   │   └── file_processor.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── context/
│   │   └── utils/
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Usage

1. **Sign Up/Login**: Create an account or login with existing credentials
2. **Start a Chat**: Begin a new conversation or continue an existing one
3. **Upload Documents**: Add PDF, Word, PowerPoint, or image files to your chat
4. **Ask Questions**: Query the AI about your uploaded documents for academic research
5. **Manage Files**: View and delete uploaded files in the current chat
6. **Chat History**: Access previous conversations from the sidebar

## Security

- All passwords are hashed using bcrypt
- JWT tokens for session management
- Input validation on all endpoints
- File type and size validation
- Rate limiting on API endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
