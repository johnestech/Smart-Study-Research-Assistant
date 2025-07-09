import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import useAuthStore from '../store/authStore';
import useChatStore from '../store/chatStore';

const ChatPage = () => {
  const { chatId } = useParams();
  const { user, logout } = useAuthStore();
  const { 
    currentChat, 
    messages, 
    isLoading, 
    loadChat, 
    sendMessage, 
    createNewChat 
  } = useChatStore();
  
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (chatId) {
      loadChat(chatId);
    } else {
      createNewChat();
    }
  }, [chatId, loadChat, createNewChat]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const messageText = input.trim();
    setInput('');
    setIsTyping(true);

    try {
      await sendMessage(messageText);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
    } finally {
      setIsTyping(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success('Logged out successfully');
    } catch (error) {
      console.error('Error logging out:', error);
      toast.error('Failed to log out');
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-gray-800">Smart Study Assistant</h2>
        </div>
        
        <div className="p-4 flex-1">
          <button
            onClick={createNewChat}
            className="w-full btn-primary mb-4"
          >
            New Chat
          </button>
          
          {/* Chat history would go here */}
          <div className="space-y-2">
            {/* Placeholder for chat history */}
            <div className="text-sm text-gray-500">
              Chat history will appear here
            </div>
          </div>
        </div>
        
        <div className="p-4 border-t">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {user?.user_metadata?.full_name?.[0] || user?.email?.[0]?.toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.user_metadata?.full_name || user?.email}
                </p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="text-gray-400 hover:text-gray-600 text-sm"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Chat messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-gray-500 mt-8">
              <h3 className="text-lg font-medium mb-2">Welcome to Smart Study Assistant</h3>
              <p>Start a conversation by asking a question or requesting help with your studies.</p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-primary-600 text-white'
                      : 'bg-white text-gray-800 shadow-sm border'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className="text-xs mt-1 opacity-70">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))
          )}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 shadow-sm border max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                <div className="flex items-center space-x-1">
                  <span className="text-sm">Assistant is typing</span>
                  <div className="loading-dots"></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Message input */}
        <div className="border-t bg-white p-4">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 input-field"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="btn-primary px-6"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
