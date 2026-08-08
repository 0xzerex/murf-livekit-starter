'use client';

import { useState, useEffect } from 'react';
import { useTheme } from 'next-themes';
import { AnimatePresence, motion } from 'motion/react';
import { ConnectionState } from 'livekit-client';
import { useSessionContext } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { AgentSessionView_01 } from '@/components/agents-ui/blocks/agent-session-view-01';
import { WelcomeView } from '@/components/app/welcome-view';
import { MicErrorCard } from '@/components/app/mic-error-card';
import { JanSahayAvatar } from '@/components/app/financial-avatar';

const MotionWelcomeView = motion.create(WelcomeView);
const MotionSessionView = motion.create(AgentSessionView_01);

const VIEW_MOTION_PROPS = {
  variants: {
    visible: { opacity: 1 },
    hidden: { opacity: 0 },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: { duration: 0.4, ease: 'easeInOut' },
};

interface ViewControllerProps {
  appConfig: AppConfig;
}

export function ViewController({ appConfig }: ViewControllerProps) {
  const session = useSessionContext();
  const { isConnected, start } = session;
  const isConnecting = session.connectionState === ConnectionState.Connecting || session.connectionState === ('connecting' as ConnectionState);
  const { resolvedTheme } = useTheme();

  const [hasEnded, setHasEnded] = useState(false);
  const [hasMicError, setHasMicError] = useState(false);
  const [wasConnected, setWasConnected] = useState(false);

  useEffect(() => {
    if (isConnected) {
      setWasConnected(true);
      setHasEnded(false);
    } else if (wasConnected && !isConnected && !isConnecting) {
      setHasEnded(true);
    }
  }, [isConnected, isConnecting, wasConnected]);

  const handleStartCall = async () => {
    setHasMicError(false);
    try {
      if (typeof navigator !== 'undefined' && navigator.mediaDevices?.getUserMedia) {
        await navigator.mediaDevices.getUserMedia({ audio: true });
      }
      start();
    } catch (err: unknown) {
      console.warn('Microphone permission check failed:', err);
      setHasMicError(true);
    }
  };

  return (
    <AnimatePresence mode="wait">
      {/* Microphone Permission Error Card */}
      {hasMicError && (
        <motion.div
          key="mic-error"
          {...VIEW_MOTION_PROPS}
          className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4"
        >
          <MicErrorCard
            onRetry={handleStartCall}
            onDismiss={() => setHasMicError(false)}
          />
        </motion.div>
      )}

      {/* State 2: Connecting View */}
      {isConnecting && !isConnected && (
        <motion.div
          key="connecting-view"
          {...VIEW_MOTION_PROPS}
          className="flex min-h-[70vh] flex-col items-center justify-center text-center p-6"
        >
          <JanSahayAvatar state="connecting" size="xl" showBadge={false} />
          <h2 className="mt-6 text-2xl font-bold text-slate-900 dark:text-white">
            Connecting to Jan Sahay AI...
          </h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-300 max-w-sm">
            Please wait while we establish your secure voice session.
          </p>
          <div className="mt-6 flex items-center gap-2 text-xs font-semibold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 px-4 py-2 rounded-full border border-amber-200 dark:border-amber-800">
            <span className="size-2 rounded-full bg-amber-500 animate-ping" />
            Initializing Citizen Assistance Agent...
          </div>
        </motion.div>
      )}

      {/* State 1 & 5: Ready / Call Ended Welcome view */}
      {!isConnected && !isConnecting && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={appConfig.startButtonText}
          onStartCall={handleStartCall}
          agentState={hasEnded ? 'ended' : 'ready'}
          hasEnded={hasEnded}
        />
      )}

      {/* State 3 & 4: Active Session View (Listening / Speaking) */}
      {isConnected && (
        <MotionSessionView
          key="session-view"
          {...VIEW_MOTION_PROPS}
          supportsChatInput={appConfig.supportsChatInput}
          supportsVideoInput={appConfig.supportsVideoInput}
          supportsScreenShare={appConfig.supportsScreenShare}
          isPreConnectBufferEnabled={appConfig.isPreConnectBufferEnabled}
          audioVisualizerType={appConfig.audioVisualizerType}
          audioVisualizerColor={
            resolvedTheme === 'dark'
              ? appConfig.audioVisualizerColorDark
              : appConfig.audioVisualizerColor
          }
          audioVisualizerColorShift={appConfig.audioVisualizerColorShift}
          audioVisualizerBarCount={appConfig.audioVisualizerBarCount}
          audioVisualizerGridRowCount={appConfig.audioVisualizerGridRowCount}
          audioVisualizerGridColumnCount={appConfig.audioVisualizerGridColumnCount}
          audioVisualizerRadialBarCount={appConfig.audioVisualizerRadialBarCount}
          audioVisualizerRadialRadius={appConfig.audioVisualizerRadialRadius}
          audioVisualizerWaveLineWidth={appConfig.audioVisualizerWaveLineWidth}
          className="fixed inset-0 z-40 bg-[#F8FAFC] dark:bg-[#0B132B]"
        />
      )}
    </AnimatePresence>
  );
}

