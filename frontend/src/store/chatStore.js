import { create } from 'zustand';
import { chatAPI } from '../services/api';

const useChatStore = create((set, get) => ({
  // State
  chats: [],
  currentChat: null,
  messages: [],
  files: [],
  isLoading: false,
  isSendingMessage: false,
  isUploadingFile: false,
  error: null,
  sidebarOpen: true,

  // Actions
  setChats: (chats) => set({ chats }),
  
  setCurrentChat: (chat) => set({ currentChat: chat }),
  
  setMessages: (messages) => set({ messages }),
  
  setFiles: (files) => set({ files }),
  
  setLoading: (isLoading) => set({ isLoading }),
  
  setSendingMessage: (isSendingMessage) => set({ isSendingMessage }),
  
  setUploadingFile: (isUploadingFile) => set({ isUploadingFile }),
  
  setError: (error) => set({ error }),
  
  clearError: () => set({ error: null }),
  
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  // Add new chat
  addChat: (chat) => set((state) => ({
    chats: [chat, ...state.chats]
  })),

  // Update existing chat
  updateChat: (chatId, updates) => set((state) => ({
    chats: state.chats.map(chat => 
      chat.id === chatId ? { ...chat, ...updates } : chat
    ),
    currentChat: state.currentChat?.id === chatId 
      ? { ...state.currentChat, ...updates } 
      : state.currentChat
  })),

  // Remove chat
  removeChat: (chatId) => set((state) => ({
    chats: state.chats.filter(chat => chat.id !== chatId),
    currentChat: state.currentChat?.id === chatId ? null : state.currentChat,
    messages: state.currentChat?.id === chatId ? [] : state.messages,
    files: state.currentChat?.id === chatId ? [] : state.files
  })),

  // Add message to current chat
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),

  // Add multiple messages
  addMessages: (newMessages) => set((state) => ({
    messages: [...state.messages, ...newMessages]
  })),

  // Add file to current chat
  addFile: (file) => set((state) => ({
    files: [...state.files, file]
  })),

  // Remove file
  removeFile: (fileId) => set((state) => ({
    files: state.files.filter(file => file.id !== fileId)
  })),

  // Update chat title after first message
  updateChatTitle: (chatId, title) => {
    get().updateChat(chatId, { title });
  },

  // Clear current chat data
  clearCurrentChatData: () => set({
    currentChat: null,
    messages: [],
    files: []
  }),

  // Load chat by ID
  loadChat: async (chatId) => {
    set({ isLoading: true });
    try {
      const response = await chatAPI.getChat(chatId);
      const chat = response.data;
      set({ 
        currentChat: chat,
        messages: chat.messages || [],
        files: chat.files || []
      });
    } catch (error) {
      console.error('Error loading chat:', error);
      set({ error: 'Failed to load chat' });
    } finally {
      set({ isLoading: false });
    }
  },

  // Create new chat
  createNewChat: async () => {
    set({ isLoading: true });
    try {
      const response = await chatAPI.createChat({ title: 'New Chat' });
      const newChat = response.data;
      set({ 
        currentChat: newChat,
        messages: [],
        files: []
      });
      get().addChat(newChat);
    } catch (error) {
      console.error('Error creating new chat:', error);
      set({ error: 'Failed to create new chat' });
    } finally {
      set({ isLoading: false });
    }
  },

  // Send message
  sendMessage: async (content) => {
    const { currentChat } = get();
    if (!currentChat) {
      throw new Error('No active chat');
    }

    set({ isSendingMessage: true });
    
    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      content,
      role: 'user',
      timestamp: new Date().toISOString()
    };
    get().addMessage(userMessage);

    try {
      const response = await chatAPI.sendMessage(currentChat.id, { content });
      const aiMessage = response.data;
      get().addMessage(aiMessage);
      
      // Update chat title if it's the first message
      if (get().messages.length === 2) {
        get().updateChatTitle(currentChat.id, content.substring(0, 50));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      set({ error: 'Failed to send message' });
      throw error;
    } finally {
      set({ isSendingMessage: false });
    }
  },

  // Reset store
  reset: () => set({
    chats: [],
    currentChat: null,
    messages: [],
    files: [],
    isLoading: false,
    isSendingMessage: false,
    isUploadingFile: false,
    error: null
  }),
}));

export default useChatStore;
