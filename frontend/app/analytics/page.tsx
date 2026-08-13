'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  BarChart3,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowLeft,
  RefreshCw,
  PhoneCall,
  User,
  ShieldAlert,
  Lock,
  Filter,
  AlertTriangle,
  FileSpreadsheet,
} from 'lucide-react';

interface CallRecord {
  id: number;
  call_id: string;
  caller_name: string;
  language: string;
  duration_seconds: number;
  status: 'success' | 'failed';
  summary: string;
  created_at: string;
}

interface AnalyticsMetrics {
  total_calls: number;
  successful_calls: number;
  failed_calls: number;
  avg_duration: number;
}

export default function AnalyticsDashboardPage() {
  const [metrics, setMetrics] = useState<AnalyticsMetrics>({
    total_calls: 0,
    successful_calls: 0,
    failed_calls: 0,
    avg_duration: 0,
  });
  const [calls, setCalls] = useState<CallRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/analytics');
      const data = await res.json();
      if (res.ok) {
        setMetrics(
          data.metrics || {
            total_calls: 0,
            successful_calls: 0,
            failed_calls: 0,
            avg_duration: 0,
          }
        );
        setCalls(data.calls || []);
      } else {
        setErrorMsg(data.error || 'Failed to load analytics data');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Error connecting to analytics database');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const filteredCalls = calls.filter((item) => {
    if (filterStatus !== 'ALL' && item.status !== filterStatus) return false;
    return true;
  });

  const formatDuration = (seconds: number) => {
    if (!seconds || seconds <= 0) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    if (mins === 0) return `${secs}s`;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 font-sans">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header Navigation */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
          <div>
            <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
              <Link
                href="/"
                className="hover:text-amber-400 transition-colors flex items-center gap-1"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Voice Agent
              </Link>
              <span>/</span>
              <Link
                href="/escalations"
                className="hover:text-amber-400 transition-colors flex items-center gap-1"
              >
                <ShieldAlert className="w-3.5 h-3.5" /> Escalations
              </Link>
              <span>/</span>
              <span className="text-amber-400 font-medium">Call Analytics</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-50 flex items-center gap-3">
              <BarChart3 className="w-8 h-8 text-blue-500" />
              Jan Sahay Call Analytics Dashboard
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Real-time success evaluation and call outcome logging for Jan Sahay AI Voice Assistant
            </p>
          </div>

          <button
            onClick={fetchAnalytics}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 transition text-sm font-medium disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh Analytics
          </button>
        </div>

        {/* Mandatory Prominent Metrics Grid (Top 4 Cards) */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Card 1: Total Calls */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Total Calls
              </p>
              <h3 className="text-3xl font-bold text-slate-100 mt-1">
                {metrics.total_calls}
              </h3>
              <p className="text-[11px] text-slate-500 mt-1">Total voice sessions</p>
            </div>
            <div className="p-3.5 bg-blue-950 text-blue-400 rounded-xl border border-blue-900/50">
              <PhoneCall className="w-6 h-6" />
            </div>
          </div>

          {/* Card 2: Successful Calls */}
          <div className="bg-slate-900/80 border border-emerald-900/40 rounded-xl p-5 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                Successful Calls
              </p>
              <h3 className="text-3xl font-bold text-emerald-300 mt-1">
                {metrics.successful_calls}
              </h3>
              <p className="text-[11px] text-emerald-600/80 dark:text-emerald-400/70 mt-1">
                Completed eligibility / escalation
              </p>
            </div>
            <div className="p-3.5 bg-emerald-950 text-emerald-400 rounded-xl border border-emerald-800/50">
              <CheckCircle2 className="w-6 h-6" />
            </div>
          </div>

          {/* Card 3: Failed Calls */}
          <div className="bg-slate-900/80 border border-rose-900/40 rounded-xl p-5 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-rose-400">
                Failed Calls
              </p>
              <h3 className="text-3xl font-bold text-rose-300 mt-1">
                {metrics.failed_calls}
              </h3>
              <p className="text-[11px] text-rose-600/80 dark:text-rose-400/70 mt-1">
                Early drop / incomplete inquiry
              </p>
            </div>
            <div className="p-3.5 bg-rose-950 text-rose-400 rounded-xl border border-rose-800/50">
              <XCircle className="w-6 h-6" />
            </div>
          </div>

          {/* Card 4: Average Duration */}
          <div className="bg-slate-900/80 border border-amber-900/40 rounded-xl p-5 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-amber-400">
                Average Duration
              </p>
              <h3 className="text-3xl font-bold text-amber-300 mt-1">
                {metrics.avg_duration}s
              </h3>
              <p className="text-[11px] text-amber-500/80 mt-1">
                ~{formatDuration(Math.round(metrics.avg_duration))} per call
              </p>
            </div>
            <div className="p-3.5 bg-amber-950 text-amber-400 rounded-xl border border-amber-800/50">
              <Clock className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Security & Data Privacy Notice */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-start gap-3 text-xs text-slate-400">
          <Lock className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-emerald-400">Caller Data Privacy Safeguard (Step 6 Policy):</span>{' '}
            Per Financial Services security guidelines, no passwords, PINs, OTPs, bank account numbers, debit/credit cards, Aadhaar, or full transcript dumps are recorded in the database or exposed on this UI. All call outcome summaries undergo automated scrubbing via <code className="bg-slate-800 px-1 py-0.5 rounded text-amber-300">sanitize_text()</code>.
          </div>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 text-sm text-slate-300 font-medium">
            <Filter className="w-4 h-4 text-blue-400" /> Filter Call Logs:
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400">Status:</span>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 focus:outline-none focus:border-blue-400 text-xs font-medium"
              >
                <option value="ALL">All Outcomes</option>
                <option value="success">Success Only</option>
                <option value="failed">Failed Only</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error message display */}
        {errorMsg && (
          <div className="bg-red-950/80 border border-red-800 text-red-200 p-4 rounded-xl text-sm flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 shrink-0 text-red-400" />
            {errorMsg}
          </div>
        )}

        {/* Recent Call Logs Table */}
        {loading ? (
          <div className="text-center py-16 text-slate-400 animate-pulse flex flex-col items-center gap-2">
            <RefreshCw className="w-6 h-6 animate-spin text-blue-400" />
            Loading call outcome logs...
          </div>
        ) : filteredCalls.length === 0 ? (
          <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-12 text-center text-slate-400 space-y-3">
            <FileSpreadsheet className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-lg font-semibold text-slate-300">No Call Logs Found</h3>
            <p className="text-sm max-w-md mx-auto text-slate-500">
              When callers connect and interact with Jan Sahay AI Voice Assistant, session duration, success status, and sanitized outcome summaries will be logged here.
            </p>
          </div>
        ) : (
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-md">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="bg-slate-950/80 text-xs uppercase tracking-wider text-slate-400 border-b border-slate-800">
                  <tr>
                    <th scope="col" className="px-6 py-4">
                      Call ID / Date
                    </th>
                    <th scope="col" className="px-6 py-4">
                      Caller Name
                    </th>
                    <th scope="col" className="px-6 py-4">
                      Language
                    </th>
                    <th scope="col" className="px-6 py-4">
                      Duration
                    </th>
                    <th scope="col" className="px-6 py-4">
                      Status
                    </th>
                    <th scope="col" className="px-6 py-4">
                      Outcome Summary
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/70">
                  {filteredCalls.map((item) => {
                    const isSuccess = item.status === 'success';

                    return (
                      <tr
                        key={item.call_id || item.id}
                        className="hover:bg-slate-800/40 transition-colors"
                      >
                        {/* Call ID & Date */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-mono text-xs font-semibold text-slate-200">
                            {item.call_id}
                          </div>
                          <div className="text-[11px] text-slate-500 mt-0.5">
                            {new Date(item.created_at).toLocaleString()}
                          </div>
                        </td>

                        {/* Caller Name */}
                        <td className="px-6 py-4 whitespace-nowrap font-medium text-slate-200">
                          <div className="flex items-center gap-2">
                            <User className="w-4 h-4 text-blue-400" />
                            {item.caller_name || 'Citizen'}
                          </div>
                        </td>

                        {/* Language */}
                        <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-300">
                          <span className="px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-slate-300">
                            {item.language || 'Hindi'}
                          </span>
                        </td>

                        {/* Duration */}
                        <td className="px-6 py-4 whitespace-nowrap text-xs font-mono font-medium text-slate-300">
                          {formatDuration(item.duration_seconds)}
                        </td>

                        {/* Status Badge */}
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${
                              isSuccess
                                ? 'bg-emerald-950 text-emerald-300 border-emerald-800'
                                : 'bg-rose-950 text-rose-300 border-rose-800'
                            }`}
                          >
                            {isSuccess ? (
                              <>
                                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                                Success
                              </>
                            ) : (
                              <>
                                <XCircle className="w-3.5 h-3.5 text-rose-400" />
                                Failed
                              </>
                            )}
                          </span>
                        </td>

                        {/* Summary */}
                        <td className="px-6 py-4 text-xs text-slate-300 max-w-md leading-relaxed">
                          {item.summary}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
