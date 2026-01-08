import React, { useState, useEffect, useRef } from 'react';
import { Users, MessageSquare, History, Send, X } from 'lucide-react';

interface ActiveUser {
  user_id: string;
  user_name: string;
  color: string;
  cursor_x?: number;
  cursor_y?: number;
}

interface ChatMessage {
  messageId: string;
  userId: string;
  userName: string;
  message: string;
  timestamp: string;
}

interface ChangeHistoryItem {
  id: string;
  change_type: string;
  entity_type: string;
  user_name: string;
  timestamp: string;
}

interface CollaborationPanelProps {
  workflowId: string;
  onClose: () => void;
}

const CollaborationPanel: React.FC<CollaborationPanelProps> = ({ workflowId, onClose }) => {
  const [activeTab, setActiveTab] = useState<'users' | 'chat' | 'history'>('users');
  const [activeUsers, setActiveUsers] = useState<ActiveUser[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [changeHistory, setChangeHistory] = useState<ChangeHistoryItem[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    connectWebSocket();
    loadChatHistory();
    loadChangeHistory();

    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, [workflowId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const connectWebSocket = () => {
    const token = localStorage.getItem('token');
    const wsUrl = `ws://localhost:8612/api/collaboration/ws/workflows/${workflowId}/collaborate?token=${token}`;
    
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('WebSocket conectado');
    };

    websocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      handleWebSocketMessage(message);
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    websocket.onclose = () => {
      console.log('WebSocket desconectado');
      // Reconectar después de 3 segundos
      setTimeout(() => connectWebSocket(), 3000);
    };

    setWs(websocket);
  };

  const handleWebSocketMessage = (message: any) => {
    switch (message.type) {
      case 'active_users':
        setActiveUsers(message.data.users);
        break;
      
      case 'user_joined':
        setActiveUsers(prev => [...prev, message.data]);
        break;
      
      case 'user_left':
        setActiveUsers(prev => prev.filter(u => u.user_id !== message.data.userId));
        break;
      
      case 'chat_message':
        setChatMessages(prev => [...prev, {
          messageId: message.data.messageId,
          userId: message.data.userId,
          userName: message.data.userName,
          message: message.data.message,
          timestamp: message.data.timestamp
        }]);
        break;
      
      case 'node_updated':
      case 'node_added':
      case 'node_deleted':
      case 'edge_added':
      case 'edge_deleted':
        // Agregar al historial
        setChangeHistory(prev => [{
          id: Date.now().toString(),
          change_type: message.type,
          entity_type: message.type.includes('node') ? 'node' : 'edge',
          user_name: message.data.userName,
          timestamp: new Date().toISOString()
        }, ...prev].slice(0, 50));
        break;
    }
  };

  const loadChatHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8612/api/collaboration/workflows/${workflowId}/chat`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const data = await response.json();
      setChatMessages(data.map((msg: any) => ({
        messageId: msg.id,
        userId: msg.user_id,
        userName: msg.user_name,
        message: msg.message,
        timestamp: msg.created_at
      })));
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const loadChangeHistory = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://localhost:8612/api/collaboration/workflows/${workflowId}/history`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const data = await response.json();
      setChangeHistory(data);
    } catch (error) {
      console.error('Error loading change history:', error);
    }
  };

  const sendMessage = () => {
    if (!newMessage.trim() || !ws) return;

    ws.send(JSON.stringify({
      type: 'chat_message',
      data: { message: newMessage }
    }));

    setNewMessage('');
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="fixed right-0 top-0 h-full w-80 bg-white shadow-lg border-l border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold">Colaboración</h2>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-100 rounded"
          aria-label="Cerrar panel"
        >
          <X size={20} />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          onClick={() => setActiveTab('users')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 ${
            activeTab === 'users' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600'
          }`}
        >
          <Users size={18} />
          <span className="text-sm">Usuarios ({activeUsers.length})</span>
        </button>
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 ${
            activeTab === 'chat' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600'
          }`}
        >
          <MessageSquare size={18} />
          <span className="text-sm">Chat</span>
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 ${
            activeTab === 'history' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-600'
          }`}
        >
          <History size={18} />
          <span className="text-sm">Historial</span>
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        {activeTab === 'users' && (
          <div className="p-4 space-y-3">
            {activeUsers.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-8">No hay usuarios activos</p>
            ) : (
              activeUsers.map((user) => (
                <div key={user.user_id} className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold"
                    style={{ backgroundColor: user.color }}
                  >
                    {user.user_name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{user.user_name}</p>
                    <p className="text-xs text-gray-500">Activo ahora</p>
                  </div>
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="flex flex-col h-full">
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chatMessages.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-8">No hay mensajes aún</p>
              ) : (
                chatMessages.map((msg) => (
                  <div key={msg.messageId} className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">{msg.userName}</span>
                      <span className="text-xs text-gray-500">{formatTimestamp(msg.timestamp)}</span>
                    </div>
                    <p className="text-sm bg-gray-100 rounded-lg p-2">{msg.message}</p>
                  </div>
                ))
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="p-4 border-t border-gray-200">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                  placeholder="Escribe un mensaje..."
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
                <button
                  onClick={sendMessage}
                  className="bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700"
                  aria-label="Enviar mensaje"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="p-4 space-y-3">
            {changeHistory.length === 0 ? (
              <p className="text-gray-500 text-sm text-center py-8">No hay cambios recientes</p>
            ) : (
              changeHistory.map((change) => (
                <div key={change.id} className="border-l-2 border-blue-600 pl-3 py-2">
                  <p className="font-medium text-sm">{change.user_name}</p>
                  <p className="text-xs text-gray-600">
                    {change.change_type.replace('_', ' ')} - {change.entity_type}
                  </p>
                  <p className="text-xs text-gray-500">{formatTimestamp(change.timestamp)}</p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default CollaborationPanel;
