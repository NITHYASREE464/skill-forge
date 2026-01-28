import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import { 
  ArrowLeft, 
  Play, 
  Send, 
  Lightbulb, 
  CheckCircle2,
  MessageSquare,
  Code2,
  BookOpen,
  Eye,
  EyeOff,
  Loader2
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const difficultyColors = {
  'Easy': 'bg-emerald-100 text-emerald-700',
  'Medium': 'bg-amber-100 text-amber-700',
  'Hard': 'bg-red-100 text-red-700'
};

export default function TaskPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const { token, refreshProfile } = useAuth();
  
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(true);
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSolution, setShowSolution] = useState(false);
  const [currentHint, setCurrentHint] = useState(0);
  
  // BRO Chat state
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    const fetchTask = async () => {
      try {
        const response = await axios.get(`${API}/skills/dsa/arrays/${taskId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setTask(response.data);
        setCode(response.data.starter_code || '');
        
        // Add welcome message from BRO
        setChatMessages([{
          role: 'bro',
          content: `Hey! Working on "${response.data.title}"? Nice choice! 👊\n\nTake your time to understand the problem first. If you get stuck, I'm here to help with hints - not answers. What have you figured out so far?`
        }]);
      } catch (error) {
        console.error('Failed to fetch task:', error);
        toast.error('Failed to load task');
        navigate('/dsa/arrays');
      } finally {
        setLoading(false);
      }
    };
    fetchTask();
  }, [taskId, token, navigate]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleRunCode = async () => {
    setIsRunning(true);
    setOutput('');
    try {
      const response = await axios.post(`${API}/code/run`, 
        { code, task_id: taskId },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setOutput(response.data.output || response.data.error || 'No output');
    } catch (error) {
      setOutput('Error running code. Please check your syntax.');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const response = await axios.post(`${API}/tasks/${taskId}/submit`,
        { task_id: taskId, code },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      if (response.data.points_earned > 0) {
        toast.success(`🎉 +${response.data.points_earned} points! Great work!`);
        await refreshProfile();
      } else {
        toast.success('Submission recorded!');
      }
      
      // Update task completion status
      setTask(prev => ({ ...prev, completed: true }));
    } catch (error) {
      toast.error('Submission failed. Try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || isChatLoading) return;

    const userMessage = chatInput.trim();
    setChatInput('');
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsChatLoading(true);

    try {
      const response = await axios.post(`${API}/bro/chat`,
        { message: userMessage, context: `Task: ${task?.title}` },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      setChatMessages(prev => [...prev, { role: 'bro', content: response.data.response }]);
    } catch (error) {
      setChatMessages(prev => [...prev, { 
        role: 'bro', 
        content: "Hmm, having some connection issues. Give me a sec and try again!" 
      }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  const showNextHint = () => {
    if (task?.hints && currentHint < task.hints.length) {
      toast.info(`Hint ${currentHint + 1}: ${task.hints[currentHint]}`);
      setCurrentHint(prev => prev + 1);
    } else {
      toast.info("No more hints available. Ask BRO for guidance!");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500">Loading task...</div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500">Task not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50" data-testid="task-page">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-full mx-auto px-4">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate('/dsa/arrays')}
                className="text-slate-600"
                data-testid="back-to-arrays-btn"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </Button>
              <div className="h-6 w-px bg-slate-200" />
              <h1 className="font-semibold text-slate-900">{task.title}</h1>
              {task.difficulty && (
                <Badge className={difficultyColors[task.difficulty]}>
                  {task.difficulty}
                </Badge>
              )}
              {task.completed && (
                <Badge className="bg-emerald-100 text-emerald-700">
                  <CheckCircle2 className="w-3 h-3 mr-1" />
                  Completed
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-slate-500">
                +{task.points} pts
              </Badge>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Three Pane Layout */}
      <div className="flex h-[calc(100vh-56px)]">
        {/* Left Pane - Problem */}
        <div className="w-1/4 min-w-[300px] border-r border-slate-200 bg-white overflow-hidden flex flex-col">
          <Tabs defaultValue="description" className="flex flex-col h-full">
            <TabsList className="w-full justify-start rounded-none border-b border-slate-200 bg-slate-50 px-4">
              <TabsTrigger value="description">
                <BookOpen className="w-4 h-4 mr-1" />
                Problem
              </TabsTrigger>
              <TabsTrigger value="solution">
                <Code2 className="w-4 h-4 mr-1" />
                Solution
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="description" className="flex-1 overflow-auto m-0 p-0">
              <ScrollArea className="h-full">
                <div className="p-6">
                  <div className="prose prose-slate prose-sm max-w-none">
                    <div className="whitespace-pre-wrap text-slate-700 leading-relaxed">
                      {task.description}
                    </div>
                  </div>
                  
                  {task.hints && task.hints.length > 0 && (
                    <div className="mt-6">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={showNextHint}
                        className="text-amber-600 border-amber-200 hover:bg-amber-50"
                        data-testid="hint-btn"
                      >
                        <Lightbulb className="w-4 h-4 mr-2" />
                        Get Hint ({currentHint}/{task.hints.length})
                      </Button>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
            
            <TabsContent value="solution" className="flex-1 overflow-auto m-0 p-0">
              <ScrollArea className="h-full">
                <div className="p-6">
                  {showSolution ? (
                    <div className="prose prose-slate prose-sm max-w-none">
                      <div className="whitespace-pre-wrap text-slate-700 leading-relaxed font-mono text-xs bg-slate-50 p-4 rounded-lg">
                        {task.solution_explanation}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-slate-500 mb-4">
                        Try solving it yourself first! Solutions are revealed after attempting.
                      </p>
                      <Button 
                        variant="outline" 
                        onClick={() => setShowSolution(true)}
                        data-testid="show-solution-btn"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Show Solution
                      </Button>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </TabsContent>
          </Tabs>
        </div>

        {/* Center Pane - Code Editor */}
        <div className="flex-1 flex flex-col bg-slate-900 min-w-[400px]">
          {/* Editor Header */}
          <div className="flex items-center justify-between px-4 py-2 bg-slate-800 border-b border-slate-700">
            <span className="text-sm text-slate-400 font-mono">solution.py</span>
            <div className="flex items-center gap-2">
              <Button 
                size="sm" 
                variant="ghost" 
                className="text-slate-300 hover:text-white hover:bg-slate-700"
                onClick={handleRunCode}
                disabled={isRunning}
                data-testid="run-code-btn"
              >
                {isRunning ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 mr-2" />
                )}
                Run
              </Button>
              <Button 
                size="sm" 
                className="bg-emerald-600 hover:bg-emerald-700 text-white"
                onClick={handleSubmit}
                disabled={isSubmitting}
                data-testid="submit-code-btn"
              >
                {isSubmitting ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                )}
                Submit
              </Button>
            </div>
          </div>
          
          {/* Code Editor Area */}
          <div className="flex-1 overflow-hidden">
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="w-full h-full p-4 bg-slate-900 text-slate-100 font-mono text-sm resize-none outline-none leading-6"
              spellCheck="false"
              data-testid="code-editor"
            />
          </div>
          
          {/* Output Panel */}
          <div className="h-1/4 min-h-[120px] border-t border-slate-700 bg-slate-800">
            <div className="px-4 py-2 border-b border-slate-700">
              <span className="text-sm text-slate-400">Output</span>
            </div>
            <ScrollArea className="h-[calc(100%-36px)]">
              <pre className="p-4 text-sm text-slate-300 font-mono whitespace-pre-wrap" data-testid="code-output">
                {output || 'Run your code to see output...'}
              </pre>
            </ScrollArea>
          </div>
        </div>

        {/* Right Pane - BRO Chat */}
        <div className="w-1/4 min-w-[300px] border-l border-slate-200 bg-white flex flex-col">
          {/* Chat Header */}
          <div className="px-4 py-3 border-b border-slate-200 flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
              <MessageSquare className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-900 text-sm">BRO</h3>
              <p className="text-xs text-slate-500">Your AI Mentor</p>
            </div>
          </div>
          
          {/* Chat Messages */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {chatMessages.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`bro-message ${msg.role === 'user' ? 'flex justify-end' : ''}`}
                >
                  <div className={`max-w-[90%] rounded-lg px-3 py-2 ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-slate-100 text-slate-700'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {isChatLoading && (
                <div className="bro-message">
                  <div className="bg-slate-100 rounded-lg px-3 py-2">
                    <Loader2 className="w-4 h-4 animate-spin text-slate-500" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
          </ScrollArea>
          
          {/* Chat Input */}
          <form onSubmit={handleChat} className="p-4 border-t border-slate-200">
            <div className="flex gap-2">
              <Input
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask BRO for help..."
                className="flex-1"
                disabled={isChatLoading}
                data-testid="bro-chat-input"
              />
              <Button 
                type="submit" 
                size="icon"
                disabled={isChatLoading || !chatInput.trim()}
                className="bg-blue-600 hover:bg-blue-700"
                data-testid="bro-send-btn"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
