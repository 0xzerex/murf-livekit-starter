'use client';

import React from 'react';
import Image from 'next/image';
import { cn } from '@/lib/shadcn/utils';

export type AgentDisplayState = 'ready' | 'connecting' | 'listening' | 'speaking' | 'ended';

interface JanSahayAvatarProps {
  state?: AgentDisplayState;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  showBadge?: boolean;
}

export function JanSahayAvatar({
  state = 'ready',
  size = 'lg',
  className,
  showBadge = true,
}: JanSahayAvatarProps) {
  const sizeMap = {
    sm: 'size-12',
    md: 'size-20',
    lg: 'size-32',
    xl: 'size-44 md:size-52',
  };

  const getRingColor = () => {
    switch (state) {
      case 'connecting':
        return 'border-amber-500 animate-spin shadow-amber-500/30';
      case 'listening':
        return 'border-emerald-600 animate-pulse shadow-emerald-500/50 ring-4 ring-emerald-400/30';
      case 'speaking':
        return 'border-[#0F4C81] animate-bounce shadow-[#0F4C81]/50 ring-4 ring-[#FF9933]/40';
      case 'ended':
        return 'border-slate-400 opacity-80';
      case 'ready':
      default:
        return 'border-[#0F4C81] shadow-[#0F4C81]/20 hover:scale-105 transition-transform';
    }
  };

  const getStateLabel = () => {
    switch (state) {
      case 'connecting':
        return { text: 'Connecting...', color: 'bg-amber-500 text-white' };
      case 'listening':
        return { text: 'Listening to you', color: 'bg-emerald-600 text-white animate-pulse' };
      case 'speaking':
        return { text: 'Jan Sahay is speaking', color: 'bg-[#0F4C81] text-white' };
      case 'ended':
        return { text: 'Call Ended', color: 'bg-slate-500 text-white' };
      case 'ready':
      default:
        return { text: 'AI Citizen Guide', color: 'bg-[#0F4C81] text-white' };
    }
  };

  const label = getStateLabel();

  return (
    <div className={cn('relative flex flex-col items-center justify-center', className)}>
      {/* Outer Glow Ring */}
      <div
        className={cn(
          'relative rounded-full border-4 p-1 transition-all duration-500 shadow-xl bg-white dark:bg-slate-800',
          sizeMap[size],
          getRingColor()
        )}
      >
        <div className="relative h-full w-full overflow-hidden rounded-full">
          <Image
            src="/jan-sahay-avatar.png"
            alt="Jan Sahay AI Assistant"
            fill
            className="object-cover"
            priority
          />
        </div>
      </div>

      {/* State Badge */}
      {showBadge && (
        <div
          className={cn(
            'mt-3 flex items-center gap-1.5 rounded-full px-3.5 py-1 text-xs font-semibold tracking-wide shadow-md transition-all duration-300',
            label.color
          )}
        >
          <span className="size-2 rounded-full bg-white animate-ping" />
          {label.text}
        </div>
      )}
    </div>
  );
}
