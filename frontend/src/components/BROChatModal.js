import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { X, Send, Mic, MicOff, MessageSquare, Loader2, FileText, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const quickPrompts = [
  { label: "Explain Two Sum", icon: "💡", message: "Can you explain the Two Sum problem and give me hints?" },
  { label: "Resume Tips", icon: "📄", message: "What are the best tips for writing a tech resume?" },
  { label: "Interview Prep", icon: "🎯", message: "How should I prepare for coding interviews?" },
  { label: "DSA Strategy", icon: "📊", message: "What's the best strategy to learn DSA effectively?" },
];

export default function BROChatModal({ isOpen, onClose }) {
  const { token, user } = useAuth();
  const [messages, setMessages] = useState([
    {
      role: 'bro',
      content: `Hey ${user?.name?.split(' ')[0] || 'there'}! 👊 I'm BRO, your AI mentor.\n\nI can help you with:\n• DSA concepts & problem hints\n• Resume reviews & tips\n• Interview preparation\n• Career guidance\n\nWhat would you like to work on today?`
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [mode, setMode] = useState('chat'); // 'chat' or 'resume'
  const chatEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API}/bro/chat`,
        { message: userMessage, context: mode === 'resume' ? 'Resume Help Mode' : 'General Chat' },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setMessages(prev => [...prev, { role: 'bro', content: response.data.response }]);
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'bro', 
        content: "Oops, had a connection hiccup. Try again?" 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickPrompt = (prompt) => {
    setInput(prompt.message);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await sendVoiceMessage(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      toast.info('Recording... Click again to stop');
    } catch (error) {
      toast.error('Microphone access denied. Please allow microphone access.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    setIsLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: '🎤 Voice message...' }]);

    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'voice.webm');
      formData.append('context', mode === 'resume' ? 'Resume Help Mode' : 'General Chat');

      const response = await axios.post(`${API}/bro/voice`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });

      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: 'user', content: response.data.transcription };
        return [...updated, { role: 'bro', content: response.data.response }];
      });
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'bro', 
        content: "Voice processing had an issue. Try typing instead!" 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4" data-testid="bro-chat-modal">
      <Card className="w-full max-w-2xl h-[600px] flex flex-col shadow-2xl border-slate-200">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-gradient-to-r from-blue-600 to-blue-700 rounded-t-lg">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
              <MessageSquare className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-white">BRO - AI Mentor</h3>
              <p className="text-xs text-blue-100">Voice + Text Support</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant={mode === 'chat' ? 'secondary' : 'ghost'}
              onClick={() => setMode('chat')}
              className={mode === 'chat' ? 'bg-white/20 text-white' : 'text-white/70 hover:text-white hover:bg-white/10'}
            >
              <MessageSquare className="w-4 h-4 mr-1" />
              Chat
            </Button>
            <Button
              size="sm"
              variant={mode === 'resume' ? 'secondary' : 'ghost'}
              onClick={() => setMode('resume')}
              className={mode === 'resume' ? 'bg-white/20 text-white' : 'text-white/70 hover:text-white hover:bg-white/10'}
            >
              <FileText className="w-4 h-4 mr-1" />
              Resume AI
            </Button>
            <Button variant="ghost" size="icon" onClick={onClose} className="text-white hover:bg-white/10">
              <X className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Quick Prompts */}
        <div className="p-3 border-b border-slate-100 bg-slate-50">
          <div className="flex gap-2 overflow-x-auto pb-1">
            {quickPrompts.map((prompt, idx) => (
              <Button
                key={idx}
                variant="outline"
                size="sm"
                onClick={() => handleQuickPrompt(prompt)}
                className="whitespace-nowrap text-xs bg-white hover:bg-blue-50 hover:border-blue-300"
              >
                <span className="mr-1">{prompt.icon}</span>
                {prompt.label}
              </Button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-4">
          <div className="space-y-4">
            {messages.map((msg, idx) => (
              <div 
                key={idx} 
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                  msg.role === 'user' 
                    ? 'bg-blue-600 text-white rounded-br-md' 
                    : 'bg-slate-100 text-slate-700 rounded-bl-md'
                }`}>
                  <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-100 rounded-2xl rounded-bl-md px-4 py-3">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>
        </ScrollArea>

        {/* Input */}
        <div className="p-4 border-t border-slate-200 bg-white rounded-b-lg">
          <form onSubmit={handleSend} className="flex gap-2">
            <Button 
              type="button" 
              size="icon" 
              variant={isRecording ? "destructive" : "outline"}
              onClick={isRecording ? stopRecording : startRecording}
              className={isRecording ? "animate-pulse" : ""}
              data-testid="bro-voice-btn"
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </Button>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={mode === 'resume' ? "Ask about resume tips..." : "Ask BRO anything..."}
              className="flex-1"
              disabled={isLoading}
              data-testid="bro-modal-input"
            />
            <Button 
              type="submit" 
              disabled={isLoading || !input.trim()} 
              className="bg-blue-600 hover:bg-blue-700"
              data-testid="bro-modal-send"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
          <p className="text-xs text-slate-400 mt-2 text-center">
            {mode === 'resume' ? '📄 Resume AI Mode - Get personalized resume advice' : '💬 Chat Mode - Ask about DSA, interviews, career tips'}
          </p>
        </div>
      </Card>
    </div>
  );
}
