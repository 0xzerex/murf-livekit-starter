'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  ShieldAlert,
  HelpCircle,
  CheckCircle2,
  Clock,
  ArrowLeft,
  RefreshCw,
  PhoneCall,
  User,
  FileText,
  AlertTriangle,
  Lock,
  Filter,
} from 'lucide-react';

interface EscalationRecord {
  reference_id: string;
  user_id: string;
  caller_name: string;
  reason_category: string;
  what_happened: string;
  agent_checks: string;
  urgency_level: string;
  language_preference: string;
  preferred_followup: string;
  status: string;
  created_at: string;
}

export default function EscalationsDashboardPage() {
  const [escalations, setEscalations] = useState<EscalationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('ALL');
  const [filterReason, setFilterReason] = useState<string>('ALL');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchEscalations = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/escalations');
      const data = await res.json();
      if (res.ok) {
        setEscalations(data.escalations || []);
      } else {
        setErrorMsg(data.error || 'Failed to fetch escalations');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Error connecting to database');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEscalations();
  }, []);

  const toggleStatus = async (referenceId: string, currentStatus: string) => {
    const newStatus = currentStatus === 'OPEN' ? 'RESOLVED' : 'OPEN';
    try {
      const res = await fetch('/api/escalations', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reference_id: referenceId, status: newStatus }),
      });
      if (res.ok) {
        setEscalations((prev) =>
          prev.map((item) =>
            item.reference_id === referenceId ? { ...item, status: newStatus } : item
          )
        );
      }
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  const filteredEscalations = escalations.filter((item) => {
    if (filterStatus !== 'ALL' && item.status !== filterStatus) return false;
    if (filterReason !== 'ALL' && item.reason_category !== filterReason) return false;
    return true;
  });

  const openCount = escalations.filter((i) => i.status === 'OPEN').length;
  const fraudCount = escalations.filter((i) => i.reason_category === 'fraud_report').length;
  const decisionCount = escalations.filter(
    (i) => i.reason_category === 'unauthorized_decision'
  ).length;

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
              <span className="text-amber-400 font-medium">Financial Services Escalations</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-slate-50 flex items-center gap-3">
              <ShieldAlert className="w-8 h-8 text-amber-500" />
              Human-Help Escalations Dashboard
            </h1>
            <p className="text-slate-400 text-sm mt-1">
              Real-time caller assistance requests routed from Jan Sahay AI Voice Assistant
            </p>
          </div>

          <button
            onClick={fetchEscalations}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 transition text-sm font-medium disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh Requests
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Total Requests
              </p>
              <h3 className="text-2xl font-bold text-slate-100 mt-1">{escalations.length}</h3>
            </div>
            <div className="p-3 bg-slate-800 text-slate-300 rounded-lg">
              <FileText className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-slate-900/80 border border-amber-900/40 rounded-xl p-4 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-amber-400">
                Open Tickets
              </p>
              <h3 className="text-2xl font-bold text-amber-300 mt-1">{openCount}</h3>
            </div>
            <div className="p-3 bg-amber-950 text-amber-400 rounded-lg border border-amber-800/50">
              <Clock className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-slate-900/80 border border-red-900/40 rounded-xl p-4 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-red-400">
                Possible Fraud Reports
              </p>
              <h3 className="text-2xl font-bold text-red-300 mt-1">{fraudCount}</h3>
            </div>
            <div className="p-3 bg-red-950 text-red-400 rounded-lg border border-red-800/50">
              <ShieldAlert className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-slate-900/80 border border-blue-900/40 rounded-xl p-4 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-blue-400">
                Decision Required
              </p>
              <h3 className="text-2xl font-bold text-blue-300 mt-1">{decisionCount}</h3>
            </div>
            <div className="p-3 bg-blue-950 text-blue-400 rounded-lg border border-blue-800/50">
              <HelpCircle className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Security Notice */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 flex items-start gap-3 text-xs text-slate-400">
          <Lock className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold text-emerald-400">Sanitized & Consent-Verified Data:</span>{' '}
            Per Financial Services security guidelines, all requests are submitted after explicit caller consent. Passwords, PINs, OTPs, full card numbers, and bank account details are automatically scrubbed prior to storage.
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 text-sm text-slate-300 font-medium">
            <Filter className="w-4 h-4 text-amber-400" /> Filter Requests:
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400">Status:</span>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 focus:outline-none focus:border-amber-400 text-xs"
              >
                <option value="ALL">All Statuses</option>
                <option value="OPEN">Open Only</option>
                <option value="RESOLVED">Resolved Only</option>
              </select>
            </div>

            <div className="flex items-center gap-2 text-xs">
              <span className="text-slate-400">Reason:</span>
              <select
                value={filterReason}
                onChange={(e) => setFilterReason(e.target.value)}
                className="bg-slate-800 text-slate-200 border border-slate-700 rounded-lg px-3 py-1.5 focus:outline-none focus:border-amber-400 text-xs"
              >
                <option value="ALL">All Reasons</option>
                <option value="fraud_report">Fraud Report</option>
                <option value="unauthorized_decision">Decision Required</option>
              </select>
            </div>
          </div>
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="bg-red-950/80 border border-red-800 text-red-200 p-4 rounded-xl text-sm flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            {errorMsg}
          </div>
        )}

        {/* Escalation Cards List */}
        {loading ? (
          <div className="text-center py-16 text-slate-400 animate-pulse">
            Loading escalation records...
          </div>
        ) : filteredEscalations.length === 0 ? (
          <div className="bg-slate-900/40 border border-slate-800/80 rounded-xl p-12 text-center text-slate-400 space-y-3">
            <CheckCircle2 className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-lg font-semibold text-slate-300">No Escalation Requests Found</h3>
            <p className="text-sm max-w-md mx-auto text-slate-500">
              When callers report potential fraud or ask for decisions requiring human approval during an AI voice session, escalation summaries will appear here.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {filteredEscalations.map((item) => {
              const isFraud = item.reason_category === 'fraud_report';
              const isOpen = item.status === 'OPEN';

              return (
                <div
                  key={item.reference_id}
                  className={`bg-slate-900 border ${
                    isOpen
                      ? isFraud
                        ? 'border-red-900/60 shadow-lg shadow-red-950/20'
                        : 'border-amber-900/60 shadow-lg shadow-amber-950/20'
                      : 'border-slate-800 opacity-75'
                  } rounded-xl p-5 transition-all`}
                >
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800 pb-4 mb-4">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-sm font-bold text-amber-400 bg-amber-950/60 border border-amber-800/60 px-3 py-1 rounded-md">
                        {item.reference_id}
                      </span>

                      <span
                        className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${
                          isFraud
                            ? 'bg-red-950 text-red-300 border-red-800'
                            : 'bg-blue-950 text-blue-300 border-blue-800'
                        }`}
                      >
                        {isFraud ? 'Fraud Report' : 'Decision Agent Cannot Make'}
                      </span>

                      <span
                        className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${
                          item.urgency_level === 'High' || item.urgency_level === 'Critical'
                            ? 'bg-rose-950 text-rose-300 border-rose-800'
                            : 'bg-amber-950 text-amber-300 border-amber-800'
                        }`}
                      >
                        Urgency: {item.urgency_level}
                      </span>
                    </div>

                    <div className="flex items-center gap-3">
                      <span className="text-xs text-slate-400">
                        {new Date(item.created_at).toLocaleString()}
                      </span>

                      <button
                        onClick={() => toggleStatus(item.reference_id, item.status)}
                        className={`px-3 py-1 rounded-lg text-xs font-bold transition flex items-center gap-1.5 ${
                          isOpen
                            ? 'bg-amber-500 hover:bg-amber-400 text-slate-950'
                            : 'bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-800'
                        }`}
                      >
                        {isOpen ? (
                          <>
                            <Clock className="w-3.5 h-3.5" /> Mark Resolved
                          </>
                        ) : (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5" /> Resolved (Reopen)
                          </>
                        )}
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                    {/* Caller Info */}
                    <div className="space-y-2">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                        <User className="w-3.5 h-3.5 text-amber-400" /> Caller Information
                      </p>
                      <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/80 space-y-1">
                        <p className="font-semibold text-slate-200">{item.caller_name}</p>
                        <p className="text-xs text-slate-400">ID / Contact: {item.user_id}</p>
                        <p className="text-xs text-amber-300 flex items-center gap-1 pt-1">
                          <PhoneCall className="w-3 h-3" /> Language: {item.language_preference} | Follow-up: {item.preferred_followup}
                        </p>
                      </div>
                    </div>

                    {/* What Happened */}
                    <div className="space-y-2">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-red-400" /> Incident Summary
                      </p>
                      <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
                        {item.what_happened}
                      </div>
                    </div>

                    {/* Agent Checks */}
                    <div className="space-y-2">
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Agent Checked
                      </p>
                      <div className="bg-slate-950/60 rounded-lg p-3 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
                        {item.agent_checks}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
