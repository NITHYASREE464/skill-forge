import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, 
  User, 
  Mail, 
  Trophy, 
  Target,
  Zap,
  Calendar,
  Settings
} from 'lucide-react';

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const getLevelBadge = (level) => {
    const colors = {
      'Beginner': 'bg-slate-100 text-slate-700',
      'Intermediate': 'bg-blue-100 text-blue-700',
      'Advanced': 'bg-violet-100 text-violet-700'
    };
    return colors[level] || colors['Beginner'];
  };

  return (
    <div className="min-h-screen bg-slate-50" data-testid="profile-page">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Button 
              variant="ghost" 
              size="sm" 
              onClick={() => navigate('/dashboard')}
              className="text-slate-600"
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Dashboard
            </Button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <div className="mb-8">
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center">
              <User className="w-10 h-10 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                {user?.name || 'Student'}
              </h1>
              <p className="text-slate-500 flex items-center gap-2 mt-1">
                <Mail className="w-4 h-4" />
                {user?.email}
              </p>
              <Badge className={`mt-2 ${getLevelBadge(user?.level)}`}>
                {user?.level || 'Beginner'}
              </Badge>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-3 gap-4 mb-8">
          <Card className="border-slate-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-amber-50 flex items-center justify-center">
                  <Trophy className="w-6 h-6 text-amber-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">Total Points</p>
                  <p className="text-2xl font-bold text-slate-900">{user?.points || 0}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center">
                  <Target className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">Target Role</p>
                  <p className="text-lg font-semibold text-slate-900">{user?.role || 'Not Set'}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200">
            <CardContent className="p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-violet-50 flex items-center justify-center">
                  <Zap className="w-6 h-6 text-violet-600" />
                </div>
                <div>
                  <p className="text-sm text-slate-500">Level</p>
                  <p className="text-lg font-semibold text-slate-900">{user?.level || 'Beginner'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Weekly Activity */}
        <Card className="border-slate-200 mb-8">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Calendar className="w-5 h-5 text-slate-500" />
              Weekly Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-slate-900">
                  {user?.weekly_activity?.leetcode || 0}
                </p>
                <p className="text-sm text-slate-500">Problems Solved</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-slate-900">
                  {user?.weekly_activity?.github || 0}
                </p>
                <p className="text-sm text-slate-500">GitHub Pushes</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-lg">
                <p className="text-2xl font-bold text-slate-900">
                  {user?.weekly_activity?.linkedin || 0}
                </p>
                <p className="text-sm text-slate-500">LinkedIn Posts</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Level Progress */}
        <Card className="border-slate-200">
          <CardHeader>
            <CardTitle className="text-lg">Level Progression</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <Badge className="bg-slate-100 text-slate-700 w-28 justify-center">
                  Beginner
                </Badge>
                <div className="flex-1 h-2 bg-slate-100 rounded-full">
                  <div 
                    className="h-full bg-slate-500 rounded-full"
                    style={{ width: user?.points >= 50 ? '100%' : `${(user?.points || 0) * 2}%` }}
                  />
                </div>
                <span className="text-sm text-slate-500 w-16 text-right">0-50 pts</span>
              </div>
              <div className="flex items-center gap-4">
                <Badge className="bg-blue-100 text-blue-700 w-28 justify-center">
                  Intermediate
                </Badge>
                <div className="flex-1 h-2 bg-slate-100 rounded-full">
                  <div 
                    className="h-full bg-blue-500 rounded-full"
                    style={{ 
                      width: user?.points >= 100 
                        ? '100%' 
                        : user?.points >= 50 
                          ? `${((user?.points - 50) / 50) * 100}%` 
                          : '0%' 
                    }}
                  />
                </div>
                <span className="text-sm text-slate-500 w-16 text-right">50-100 pts</span>
              </div>
              <div className="flex items-center gap-4">
                <Badge className="bg-violet-100 text-violet-700 w-28 justify-center">
                  Advanced
                </Badge>
                <div className="flex-1 h-2 bg-slate-100 rounded-full">
                  <div 
                    className="h-full bg-violet-500 rounded-full"
                    style={{ 
                      width: user?.points >= 100 
                        ? `${Math.min(((user?.points - 100) / 100) * 100, 100)}%` 
                        : '0%' 
                    }}
                  />
                </div>
                <span className="text-sm text-slate-500 w-16 text-right">100+ pts</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
