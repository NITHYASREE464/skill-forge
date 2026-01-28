import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Code2, 
  Trophy, 
  Target, 
  Zap, 
  ChevronRight, 
  LogOut, 
  User,
  BookOpen,
  MessageSquare
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, token, logout } = useAuth();
  const [arraysData, setArraysData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API}/skills/dsa/arrays`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setArraysData(response.data);
      } catch (error) {
        console.error('Failed to fetch arrays data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getLevelBadge = (level) => {
    const colors = {
      'Beginner': 'bg-slate-100 text-slate-700',
      'Intermediate': 'bg-blue-100 text-blue-700',
      'Advanced': 'bg-violet-100 text-violet-700'
    };
    return colors[level] || colors['Beginner'];
  };

  const progressPercent = arraysData 
    ? Math.round((arraysData.completed_tasks / arraysData.total_tasks) * 100) 
    : 0;

  return (
    <div className="min-h-screen bg-slate-50" data-testid="dashboard-page">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
                <Code2 className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold text-slate-900">SkillForge</span>
            </div>
            <div className="flex items-center gap-4">
              <Link to="/profile">
                <Button variant="ghost" size="sm" className="text-slate-600" data-testid="profile-btn">
                  <User className="w-4 h-4 mr-2" />
                  Profile
                </Button>
              </Link>
              <Button variant="ghost" size="sm" onClick={handleLogout} className="text-slate-600" data-testid="logout-btn">
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Welcome back, {user?.name?.split(' ')[0]}!
          </h1>
          <p className="text-slate-500 mt-1">Continue your {user?.role} preparation journey</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="border-slate-200">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">Total Points</p>
                  <p className="text-2xl font-bold text-slate-900">{user?.points || 0}</p>
                </div>
                <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
                  <Trophy className="w-5 h-5 text-amber-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">Current Level</p>
                  <Badge className={`mt-1 ${getLevelBadge(user?.level)}`}>
                    {user?.level || 'Beginner'}
                  </Badge>
                </div>
                <div className="w-10 h-10 rounded-lg bg-violet-50 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-violet-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">Target Role</p>
                  <p className="text-lg font-semibold text-slate-900">{user?.role || 'Not Set'}</p>
                </div>
                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                  <Target className="w-5 h-5 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-500">Tasks Done</p>
                  <p className="text-2xl font-bold text-slate-900">
                    {arraysData?.completed_tasks || 0}/{arraysData?.total_tasks || 0}
                  </p>
                </div>
                <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-emerald-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Active Tracks */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">Your Learning Tracks</h2>
          
          <Card className="border-slate-200 task-card" data-testid="dsa-track-card">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center">
                    <Code2 className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Data Structures & Algorithms</h3>
                    <p className="text-sm text-slate-500 mt-1">Master DSA for coding interviews</p>
                    <div className="flex items-center gap-4 mt-3">
                      <Badge className="bg-emerald-100 text-emerald-700">Arrays</Badge>
                      <Badge variant="outline" className="text-slate-400">Strings (Coming Soon)</Badge>
                      <Badge variant="outline" className="text-slate-400">Linked Lists (Coming Soon)</Badge>
                    </div>
                  </div>
                </div>
                <Link to="/dsa/arrays">
                  <Button className="bg-blue-600 hover:bg-blue-700" data-testid="continue-dsa-btn">
                    Continue
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </div>
              
              <div className="mt-6">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-slate-600">Arrays Module Progress</span>
                  <span className="font-medium text-slate-900">{progressPercent}%</span>
                </div>
                <Progress value={progressPercent} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* BRO Mentor Promo */}
        <Card className="border-slate-200 bg-gradient-to-r from-slate-50 to-blue-50" data-testid="bro-promo-card">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">Meet BRO – Your AI Mentor</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    Get hints, explanations, and interview tips. Available in every task!
                  </p>
                </div>
              </div>
              <Badge className="bg-blue-100 text-blue-700">New</Badge>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
