import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Code2, Trophy, Target, Zap, ChevronRight, LogOut, User,
  BookOpen, MessageSquare, FileText, TrendingUp, Flame, Database, Brain, Cpu
} from 'lucide-react';
import JobTrendsPopup from '@/components/JobTrendsPopup';
import BROChatModal from '@/components/BROChatModal';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user, token, logout } = useAuth();
  const [dsaTracks, setDsaTracks] = useState([]);
  const [readiness, setReadiness] = useState(null);
  const [showTrends, setShowTrends] = useState(false);
  const [showBRO, setShowBRO] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [dsaRes, readinessRes] = await Promise.all([
          axios.get(`${API}/skills/dsa`, { headers: { Authorization: `Bearer ${token}` }}),
          axios.get(`${API}/readiness`, { headers: { Authorization: `Bearer ${token}` }})
        ]);
        setDsaTracks(dsaRes.data.tracks);
        setReadiness(readinessRes.data);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    
    // Show trends popup after 2 seconds
    const timer = setTimeout(() => setShowTrends(true), 2000);
    return () => clearTimeout(timer);
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

  const roleIcons = {
    'SDE': Code2,
    'Data Analyst': Database,
    'Data Scientist': Brain,
    'ML Engineer': Cpu
  };
  const RoleIcon = roleIcons[user?.role] || Code2;

  const totalCompleted = dsaTracks.reduce((sum, t) => sum + t.completed_tasks, 0);
  const totalTasks = dsaTracks.reduce((sum, t) => sum + t.total_tasks, 0);

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
            <div className="flex items-center gap-2">
              <Link to="/readiness">
                <Button variant="ghost" size="sm" className="text-slate-600" data-testid="readiness-btn">
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Readiness
                </Button>
              </Link>
              <Link to="/resume">
                <Button variant="ghost" size="sm" className="text-slate-600" data-testid="resume-btn">
                  <FileText className="w-4 h-4 mr-2" />
                  Resume
                </Button>
              </Link>
              <Link to="/profile">
                <Button variant="ghost" size="sm" className="text-slate-600" data-testid="profile-btn">
                  <User className="w-4 h-4 mr-2" />
                  Profile
                </Button>
              </Link>
              <Button variant="ghost" size="sm" onClick={handleLogout} className="text-slate-600" data-testid="logout-btn">
                <LogOut className="w-4 h-4" />
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
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
                  <Trophy className="w-5 h-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Points</p>
                  <p className="text-xl font-bold text-slate-900">{user?.points || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-orange-50 flex items-center justify-center">
                  <Flame className="w-5 h-5 text-orange-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Streak</p>
                  <p className="text-xl font-bold text-slate-900">{readiness?.streak?.current || 0} days</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-violet-50 flex items-center justify-center">
                  <Zap className="w-5 h-5 text-violet-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Level</p>
                  <Badge className={`mt-1 ${getLevelBadge(user?.level)}`}>
                    {user?.level || 'Beginner'}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                  <RoleIcon className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Role</p>
                  <p className="text-sm font-semibold text-slate-900">{user?.role}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200">
            <CardContent className="p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
                  <Target className="w-5 h-5 text-emerald-600" />
                </div>
                <div>
                  <p className="text-xs text-slate-500">Readiness</p>
                  <p className="text-xl font-bold text-slate-900">{readiness?.overall_readiness || 0}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Learning Tracks */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* DSA Track */}
          <Card className="border-slate-200 task-card" data-testid="dsa-track-card">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center">
                    <Code2 className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">DSA Track</h3>
                    <p className="text-sm text-slate-500">{dsaTracks.length} modules available</p>
                  </div>
                </div>
                <Link to="/dsa">
                  <Button className="bg-blue-600 hover:bg-blue-700" data-testid="continue-dsa-btn">
                    Continue
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </div>
              <div className="flex flex-wrap gap-2 mb-4">
                {dsaTracks.slice(0, 4).map((track) => (
                  <Badge key={track.id} variant={track.completed_tasks > 0 ? "default" : "outline"} 
                    className={track.completed_tasks > 0 ? "bg-emerald-100 text-emerald-700" : "text-slate-400"}>
                    {track.name}
                  </Badge>
                ))}
                {dsaTracks.length > 4 && <Badge variant="outline">+{dsaTracks.length - 4} more</Badge>}
              </div>
              <Progress value={(totalCompleted / totalTasks) * 100} className="h-2" />
              <p className="text-xs text-slate-500 mt-2">{totalCompleted}/{totalTasks} tasks completed</p>
            </CardContent>
          </Card>

          {/* Data Analytics Track */}
          <Card className="border-slate-200 task-card" data-testid="analytics-track-card">
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-lg bg-emerald-50 flex items-center justify-center">
                    <Database className="w-6 h-6 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Data Analytics</h3>
                    <p className="text-sm text-slate-500">SQL, Excel, EDA</p>
                  </div>
                </div>
                <Link to="/analytics">
                  <Button variant="outline" data-testid="analytics-btn">
                    Explore
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </div>
              <div className="flex flex-wrap gap-2">
                <Badge className="bg-emerald-100 text-emerald-700">SQL</Badge>
                <Badge variant="outline" className="text-slate-400">Excel</Badge>
                <Badge variant="outline" className="text-slate-400">EDA</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Resume Builder */}
          <Card className="border-slate-200 task-card">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-lg bg-violet-50 flex items-center justify-center">
                    <FileText className="w-6 h-6 text-violet-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Resume Builder</h3>
                    <p className="text-sm text-slate-500">Company-specific ATS resumes</p>
                  </div>
                </div>
                <Link to="/resume">
                  <Button variant="outline" data-testid="resume-builder-btn">
                    Build
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Placement Readiness */}
          <Card className="border-slate-200 task-card">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-lg bg-amber-50 flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-amber-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">Placement Readiness</h3>
                    <p className="text-sm text-slate-500">Track your interview prep</p>
                  </div>
                </div>
                <Link to="/readiness">
                  <Button variant="outline" data-testid="readiness-dashboard-btn">
                    View
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* BRO Mentor Promo */}
        <Card 
          className="border-slate-200 bg-gradient-to-r from-slate-50 to-blue-50 cursor-pointer hover:shadow-md transition-shadow" 
          data-testid="bro-promo-card"
          onClick={() => setShowBRO(true)}
        >
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-blue-600 flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900">Meet BRO – Your AI Mentor</h3>
                  <p className="text-sm text-slate-500 mt-1">
                    Voice + Text support. Get hints, resume help, and interview tips!
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge className="bg-blue-100 text-blue-700">Voice Mode</Badge>
                <Badge className="bg-emerald-100 text-emerald-700">Resume AI</Badge>
                <Button className="bg-blue-600 hover:bg-blue-700 ml-2" data-testid="open-bro-btn">
                  Chat Now
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>

      {/* Job Trends Popup */}
      {showTrends && <JobTrendsPopup onClose={() => setShowTrends(false)} />}
    </div>
  );
}
