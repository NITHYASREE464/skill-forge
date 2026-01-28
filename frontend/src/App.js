import React from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { AuthProvider, useAuth } from "@/context/AuthContext";
import LoginPage from "@/pages/LoginPage";
import RoleSelectionPage from "@/pages/RoleSelectionPage";
import DashboardPage from "@/pages/DashboardPage";
import ArraysModulePage from "@/pages/ArraysModulePage";
import TaskPage from "@/pages/TaskPage";
import ProfilePage from "@/pages/ProfilePage";

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-slate-500">Loading...</div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  // If user has no role, redirect to role selection
  if (!user.role && window.location.pathname !== '/select-role') {
    return <Navigate to="/select-role" replace />;
  }
  
  return children;
};

const RoleGuard = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-slate-500">Loading...</div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  // If user already has role, redirect to dashboard
  if (user.role) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return children;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/select-role" element={
            <RoleGuard>
              <RoleSelectionPage />
            </RoleGuard>
          } />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } />
          <Route path="/dsa/arrays" element={
            <ProtectedRoute>
              <ArraysModulePage />
            </ProtectedRoute>
          } />
          <Route path="/task/:taskId" element={
            <ProtectedRoute>
              <TaskPage />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
        <Toaster position="top-right" />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
