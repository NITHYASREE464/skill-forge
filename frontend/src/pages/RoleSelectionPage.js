import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { toast } from 'sonner';
import { Code2, Database, Brain, Cpu, ChevronRight, Check } from 'lucide-react';

const roles = [
  {
    id: 'SDE',
    title: 'Software Development Engineer',
    shortTitle: 'SDE',
    description: 'Build scalable systems, master DSA, and crack coding interviews',
    icon: Code2,
    tracks: ['Data Structures & Algorithms', 'System Design', 'OOP Concepts'],
    color: 'blue'
  },
  {
    id: 'Data Analyst',
    title: 'Data Analyst',
    shortTitle: 'Data Analyst',
    description: 'Transform data into insights with SQL, Python, and visualization',
    icon: Database,
    tracks: ['SQL Mastery', 'Python for Data', 'Visualization'],
    color: 'emerald'
  },
  {
    id: 'Data Scientist',
    title: 'Data Scientist',
    shortTitle: 'Data Scientist',
    description: 'Build ML models and solve complex business problems',
    icon: Brain,
    tracks: ['Statistics', 'Machine Learning', 'Deep Learning'],
    color: 'violet'
  },
  {
    id: 'ML Engineer',
    title: 'ML Engineer',
    shortTitle: 'ML Engineer',
    description: 'Deploy ML systems at scale with production-grade pipelines',
    icon: Cpu,
    tracks: ['MLOps', 'Model Optimization', 'Distributed Systems'],
    color: 'amber'
  }
];

const colorClasses = {
  blue: { bg: 'bg-blue-50', border: 'border-blue-200', icon: 'text-blue-600', selected: 'border-blue-500 bg-blue-50' },
  emerald: { bg: 'bg-emerald-50', border: 'border-emerald-200', icon: 'text-emerald-600', selected: 'border-emerald-500 bg-emerald-50' },
  violet: { bg: 'bg-violet-50', border: 'border-violet-200', icon: 'text-violet-600', selected: 'border-violet-500 bg-violet-50' },
  amber: { bg: 'bg-amber-50', border: 'border-amber-200', icon: 'text-amber-600', selected: 'border-amber-500 bg-amber-50' }
};

export default function RoleSelectionPage() {
  const navigate = useNavigate();
  const { user, updateRole } = useAuth();
  const [selectedRole, setSelectedRole] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleContinue = async () => {
    if (!selectedRole) {
      toast.error('Please select a role to continue');
      return;
    }
    setIsLoading(true);
    try {
      await updateRole(selectedRole);
      toast.success('Profile setup complete!');
      navigate('/dashboard');
    } catch (error) {
      toast.error('Failed to save role. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 py-12 px-4" data-testid="role-selection-page">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
            Hey {user?.name?.split(' ')[0] || 'there'}! What's your goal?
          </h1>
          <p className="text-slate-500 mt-3 text-lg">
            Choose your target role to unlock personalized learning tracks
          </p>
        </div>

        {/* Role Cards */}
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          {roles.map((role) => {
            const Icon = role.icon;
            const colors = colorClasses[role.color];
            const isSelected = selectedRole === role.id;

            return (
              <Card
                key={role.id}
                className={`cursor-pointer transition-all duration-150 border-2 ${
                  isSelected ? colors.selected : 'border-slate-200 hover:border-slate-300'
                }`}
                onClick={() => setSelectedRole(role.id)}
                data-testid={`role-card-${role.id.toLowerCase().replace(' ', '-')}`}
              >
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className={`p-3 rounded-lg ${colors.bg}`}>
                      <Icon className={`w-6 h-6 ${colors.icon}`} />
                    </div>
                    {isSelected && (
                      <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </div>
                  <h3 className="font-semibold text-slate-900 mt-4 text-lg">{role.shortTitle}</h3>
                  <p className="text-slate-500 text-sm mt-1">{role.description}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {role.tracks.map((track) => (
                      <span
                        key={track}
                        className="text-xs px-2 py-1 bg-slate-100 text-slate-600 rounded-md"
                      >
                        {track}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Continue Button */}
        <div className="flex justify-center">
          <Button
            size="lg"
            onClick={handleContinue}
            disabled={!selectedRole || isLoading}
            className="bg-blue-600 hover:bg-blue-700 px-8"
            data-testid="role-continue-btn"
          >
            {isLoading ? 'Saving...' : 'Continue to Dashboard'}
            <ChevronRight className="w-4 h-4 ml-2" />
          </Button>
        </div>

        <p className="text-center text-xs text-slate-400 mt-6">
          You can change your role later from settings
        </p>
      </div>
    </div>
  );
}
