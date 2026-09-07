import React, { useState, useEffect } from 'react';
import { SafetyBanner } from './components/SafetyBanner';
import { Sidebar } from './components/Sidebar';
import { OverviewPage } from './pages/OverviewPage';
import { PriorityQueuePage } from './pages/PriorityQueuePage';
import { PatientDetailPage } from './pages/PatientDetailPage';
import { AlertsPage } from './pages/AlertsPage';
import { TasksPage } from './pages/TasksPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { ModelPerformancePage } from './pages/ModelPerformancePage';
import { DataQualityPage } from './pages/DataQualityPage';
import { SimulationPage } from './pages/SimulationPage';
import { StakeholderPage } from './pages/StakeholderPage';
import { AuditPage } from './pages/AuditPage';
import { SystemHealthPage } from './pages/SystemHealthPage';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [selectedPatientId, setSelectedPatientId] = useState<string>('REC-001');
  const [unresolvedTasksCount, setUnresolvedTasksCount] = useState<number>(0);
  const [activeAlertsCount, setActiveAlertsCount] = useState<number>(0);

  // Poll counters periodically for badge indicators
  useEffect(() => {
    const fetchBadges = async () => {
      try {
        const sum = await api.getDashboardSummary();
        setUnresolvedTasksCount(sum.unresolved_tasks_count || 0);
        setActiveAlertsCount(sum.active_high_priority_reviews || 0);
      } catch (e) {
        // Degraded or local development state
      }
    };
    fetchBadges();
  }, [currentTab]);

  const handleSelectPatient = (patientId: string) => {
    setSelectedPatientId(patientId);
    setCurrentTab('patient');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Pinned Clinical Safety Banner */}
      <SafetyBanner />

      {/* Main App Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Navigation */}
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          unresolvedCount={unresolvedTasksCount}
          activeAlertsCount={activeAlertsCount}
        />

        {/* Dynamic Page View Container */}
        <main className="flex-1 overflow-y-auto p-6 bg-slate-950">
          <div className="max-w-7xl mx-auto">
            {currentTab === 'overview' && (
              <OverviewPage onSelectPatient={handleSelectPatient} />
            )}

            {currentTab === 'queue' && (
              <PriorityQueuePage onSelectPatient={handleSelectPatient} />
            )}

            {currentTab === 'patient' && (
              <PatientDetailPage
                patientId={selectedPatientId}
                onBack={() => setCurrentTab('queue')}
              />
            )}

            {currentTab === 'alerts' && (
              <AlertsPage onSelectPatient={handleSelectPatient} />
            )}

            {currentTab === 'tasks' && (
              <TasksPage onSelectPatient={handleSelectPatient} />
            )}

            {currentTab === 'analytics' && (
              <AnalyticsPage />
            )}

            {currentTab === 'model' && (
              <ModelPerformancePage />
            )}

            {currentTab === 'data-quality' && (
              <DataQualityPage onSelectPatient={handleSelectPatient} />
            )}

            {currentTab === 'simulation' && (
              <SimulationPage />
            )}

            {currentTab === 'stakeholder' && (
              <StakeholderPage />
            )}

            {currentTab === 'audit' && (
              <AuditPage />
            )}

            {currentTab === 'health' && (
              <SystemHealthPage />
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default App;
