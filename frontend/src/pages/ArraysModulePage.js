import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft, 
  Code2, 
  BookOpen, 
  Bug, 
  Lightbulb,
  CheckCircle2,
  Circle,
  ChevronRight
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const difficultyColors = {
  'Easy': 'bg-emerald-100 text-emerald-700',
  'Medium': 'bg-amber-100 text-amber-700',
  'Hard': 'bg-red-100 text-red-700'
};

const typeIcons = {
  'coding': Code2,
  'concept': BookOpen,
  'debugging': Bug
};

export default function ArraysModulePage() {
  const navigate = useNavigate();
  const { token } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await axios.get(`${API}/skills/dsa/arrays`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setData(response.data);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchTasks();
  }, [token]);

  const filterTasks = (type) => {
    if (!data?.tasks) return [];
    if (type === 'all') return data.tasks;
    return data.tasks.filter(t => t.type === type);
  };

  const progressPercent = data 
    ? Math.round((data.completed_tasks / data.total_tasks) * 100) 
    : 0;

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-slate-500">Loading tasks...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50" data-testid="arrays-module-page">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => navigate('/dashboard')}
                className="text-slate-600"
                data-testid="back-btn"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Dashboard
              </Button>
            </div>
            <Badge className="bg-blue-100 text-blue-700">DSA Track</Badge>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Module Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
              <Code2 className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Arrays</h1>
          </div>
          <p className="text-slate-500 mt-2">
            Master array operations - the foundation of coding interviews. Learn patterns, solve problems, and build confidence.
          </p>
          
          {/* Progress */}
          <div className="mt-6 bg-white rounded-lg border border-slate-200 p-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-slate-600">Module Progress</span>
              <span className="font-medium text-slate-900">
                {data?.completed_tasks || 0} of {data?.total_tasks || 0} completed
              </span>
            </div>
            <Progress value={progressPercent} className="h-2" />
          </div>
        </div>

        {/* Task Tabs */}
        <Tabs defaultValue="all" className="mb-6" onValueChange={setActiveTab}>
          <TabsList className="bg-white border border-slate-200">
            <TabsTrigger value="all" data-testid="tab-all">
              All Tasks ({data?.tasks?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="coding" data-testid="tab-coding">
              <Code2 className="w-4 h-4 mr-1" />
              Coding
            </TabsTrigger>
            <TabsTrigger value="concept" data-testid="tab-concept">
              <BookOpen className="w-4 h-4 mr-1" />
              Concepts
            </TabsTrigger>
            <TabsTrigger value="debugging" data-testid="tab-debugging">
              <Bug className="w-4 h-4 mr-1" />
              Debug
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Task List */}
        <div className="space-y-3">
          {filterTasks(activeTab).map((task) => {
            const TypeIcon = typeIcons[task.type] || Code2;
            return (
              <Card 
                key={task.id} 
                className={`border-slate-200 task-card ${task.completed ? 'bg-emerald-50/30' : ''}`}
                data-testid={`task-card-${task.id}`}
              >
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        task.completed ? 'bg-emerald-100' : 'bg-slate-100'
                      }`}>
                        {task.completed ? (
                          <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                        ) : (
                          <TypeIcon className="w-5 h-5 text-slate-500" />
                        )}
                      </div>
                      <div>
                        <h3 className="font-medium text-slate-900">{task.title}</h3>
                        <div className="flex items-center gap-2 mt-1">
                          {task.difficulty && (
                            <Badge className={difficultyColors[task.difficulty]}>
                              {task.difficulty}
                            </Badge>
                          )}
                          <span className="text-xs text-slate-400">
                            +{task.points} pts
                          </span>
                          {task.attempts > 0 && (
                            <span className="text-xs text-slate-400">
                              • {task.attempts} attempt{task.attempts > 1 ? 's' : ''}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <Link to={`/task/${task.id}`}>
                      <Button 
                        variant={task.completed ? 'outline' : 'default'}
                        className={task.completed ? '' : 'bg-blue-600 hover:bg-blue-700'}
                        data-testid={`start-task-${task.id}`}
                      >
                        {task.completed ? 'Review' : 'Start'}
                        <ChevronRight className="w-4 h-4 ml-1" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {filterTasks(activeTab).length === 0 && (
          <div className="text-center py-12 text-slate-500">
            No tasks found in this category
          </div>
        )}

        {/* Tips Card */}
        <Card className="border-slate-200 mt-8 bg-amber-50/50">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center">
                <Lightbulb className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <h3 className="font-semibold text-slate-900">Pro Tips for Arrays</h3>
                <ul className="text-sm text-slate-600 mt-2 space-y-1">
                  <li>• Two-pointer technique solves many array problems efficiently</li>
                  <li>• Hash maps can reduce O(n²) to O(n) in lookup problems</li>
                  <li>• Always consider edge cases: empty array, single element, duplicates</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
