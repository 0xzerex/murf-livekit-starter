'use client';

import React from 'react';
import { WarningIcon, ArrowClockwiseIcon, ShieldCheckIcon } from '@phosphor-icons/react';
import { Button } from '@/components/ui/button';

interface MicErrorCardProps {
  onRetry: () => void;
  onDismiss?: () => void;
}

export function MicErrorCard({ onRetry, onDismiss }: MicErrorCardProps) {
  return (
    <div className="mx-auto my-6 max-w-lg rounded-2xl border-2 border-red-500/30 bg-white p-6 shadow-xl dark:bg-slate-900">
      <div className="flex items-start gap-4">
        <div className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-red-100 text-red-600 dark:bg-red-950/60 dark:text-red-400">
          <WarningIcon size={28} weight="bold" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">
            Microphone Access Required
          </h3>
          <p className="mt-1 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
            Jan Sahay Voice Assistant needs permission to use your microphone so you can ask questions by voice.
          </p>

          <div className="mt-4 rounded-xl border border-amber-200 bg-amber-50/70 p-3.5 text-xs text-amber-900 dark:border-amber-900/40 dark:bg-amber-950/30 dark:text-amber-200">
            <p className="font-semibold text-amber-800 dark:text-amber-300">
              How to enable your microphone:
            </p>
            <ol className="mt-2 space-y-1.5 list-decimal pl-4">
              <li>
                Click the <strong>🔒 Lock icon</strong> or <strong>Tune icon</strong> on the left side of your browser address bar.
              </li>
              <li>
                Find <strong>Microphone</strong> in the site settings popup.
              </li>
              <li>
                Change permission to <strong>Allow</strong>.
              </li>
              <li>
                Click <strong>Retry Permission</strong> below to start talking with Jan Sahay.
              </li>
            </ol>
          </div>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <Button
              onClick={onRetry}
              className="flex items-center gap-2 bg-[#0F4C81] text-white hover:bg-[#0c3c66]"
            >
              <ArrowClockwiseIcon size={18} weight="bold" />
              Retry Permission
            </Button>
            {onDismiss && (
              <Button onClick={onDismiss} variant="outline" className="text-slate-600">
                Dismiss
              </Button>
            )}
          </div>

          <div className="mt-4 flex items-center gap-1.5 text-[11px] text-slate-500">
            <ShieldCheckIcon size={14} className="text-emerald-600" />
            Your voice audio is encrypted & privacy protected.
          </div>
        </div>
      </div>
    </div>
  );
}
