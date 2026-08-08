import React from 'react';
import {
  ShieldCheckIcon,
  LockKeyIcon,
  BankIcon,
  WalletIcon,
  HeadsetIcon,
  MicrophoneIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  SparkleIcon,
} from '@phosphor-icons/react';
import { Button } from '@/components/ui/button';
import { JanSahayAvatar, type AgentDisplayState } from '@/components/app/financial-avatar';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
  agentState?: AgentDisplayState;
  hasEnded?: boolean;
}

export const WelcomeView = React.forwardRef<HTMLDivElement, React.ComponentProps<'div'> & WelcomeViewProps>(
  ({ startButtonText, onStartCall, agentState = 'ready', hasEnded = false, className, ...props }, ref) => {
    const featureCards = [
      {
        id: 'fraud',
        title: 'Fraud Prevention & Cyber Safety',
        icon: <LockKeyIcon size={26} className="text-[#0F4C81] dark:text-blue-400" />,
        color: 'border-l-4 border-l-[#0F4C81]',
        desc: 'Instant guidance on reporting UPI scams, phishing, fake calls, and OTP protection.',
        badge: 'Popular',
      },
      {
        id: 'schemes',
        title: 'Government Schemes & Benefits',
        icon: <BankIcon size={26} className="text-[#2E7D32] dark:text-emerald-400" />,
        color: 'border-l-4 border-l-[#2E7D32]',
        desc: 'Check eligibility & application steps for PM Kisan, Ayushman Bharat, pension & housing schemes.',
        badge: 'Public Welfare',
      },
      {
        id: 'finance',
        title: 'Financial & Banking Literacy',
        icon: <WalletIcon size={26} className="text-[#FF9933] dark:text-amber-400" />,
        color: 'border-l-4 border-l-[#FF9933]',
        desc: 'Simple explanations for bank loans, savings accounts, digital payment safety, and investments.',
        badge: 'Financial Awareness',
      },
      {
        id: 'complaint',
        title: 'Complaint Assistance & Helplines',
        icon: <HeadsetIcon size={26} className="text-[#0F4C81] dark:text-blue-400" />,
        color: 'border-l-4 border-l-[#0F4C81]',
        desc: 'Step-by-step help for registering cybercrime complaints (1930) and banking dispute resolution.',
        badge: 'Helpline Guide',
      },
    ];

    const promptChips = [
      'How do I report UPI fraud?',
      'Which government schemes am I eligible for?',
      'Explain PM Kisan scheme details.',
      'How can I avoid online financial scams?',
      'What should I do if someone asks for my OTP?',
    ];

    const scrollToServices = () => {
      document.getElementById('services')?.scrollIntoView({ behavior: 'smooth' });
    };

    return (
      <div ref={ref} className="w-full min-h-screen py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto flex flex-col justify-between">
        {/* Main Hero & Voice Section */}
        <section className="flex flex-col items-center justify-center text-center mt-4 mb-10">
          {/* Avatar and Glowing Mic Indicator */}
          <div className="relative mb-6">
            <JanSahayAvatar state={hasEnded ? 'ended' : agentState} size="xl" showBadge={false} />
            <div className="absolute -bottom-2 right-2 bg-[#2E7D32] text-white p-2 rounded-full shadow-lg border-2 border-white dark:border-slate-800 animate-pulse">
              <MicrophoneIcon size={20} weight="bold" />
            </div>
          </div>

          {/* Call Ended Alert Banner */}
          {hasEnded && (
            <div className="mb-6 rounded-2xl border border-slate-300 bg-white p-4 shadow-md dark:border-slate-700 dark:bg-slate-800 max-w-md">
              <div className="flex items-center gap-2 justify-center text-slate-800 dark:text-slate-100 font-bold">
                <CheckCircleIcon size={22} className="text-emerald-600" />
                Conversation Ended
              </div>
              <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
                Thank you for using Jan Sahay. You can start a new voice session anytime.
              </p>
            </div>
          )}

          {/* Title & Subtitle */}
          <h1 className="text-3xl sm:text-5xl font-black text-slate-900 dark:text-white tracking-tight flex items-center justify-center gap-2">
            <span>🛡️ Jan Sahay</span>
            <span className="text-sm font-semibold text-[#FF9933] bg-amber-50 dark:bg-amber-950/60 px-2.5 py-1 rounded-full border border-amber-200 dark:border-amber-800">
              जन सहाय
            </span>
          </h1>

          <p className="mt-4 text-slate-600 dark:text-slate-300 max-w-2xl text-base sm:text-lg leading-relaxed font-normal">
            Get instant guidance on government schemes, financial literacy, fraud prevention, cyber safety, banking, and digital payments through secure AI-powered voice conversations.
          </p>

          {/* CTA Buttons */}
          <div className="mt-8 flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
            <Button
              size="lg"
              onClick={onStartCall}
              className="w-full sm:w-72 h-14 rounded-full bg-[#0F4C81] hover:bg-[#0b3860] text-white font-bold text-base shadow-xl shadow-[#0F4C81]/30 flex items-center justify-center gap-2.5 transition-all hover:scale-105"
            >
              <MicrophoneIcon size={22} weight="fill" className="text-[#FF9933]" />
              {hasEnded ? '🔄 Start Again' : startButtonText}
            </Button>

            <Button
              variant="outline"
              size="lg"
              onClick={scrollToServices}
              className="w-full sm:w-44 h-14 rounded-full border-2 border-slate-300 dark:border-slate-700 font-semibold text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              Learn More
            </Button>
          </div>

          {/* Clickable Example Prompt Chips */}
          <div className="mt-10 w-full max-w-3xl">
            <div className="flex items-center justify-center gap-1.5 text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
              <SparkleIcon size={14} className="text-[#FF9933]" />
              Try Asking By Voice:
            </div>
            <div className="flex flex-wrap items-center justify-center gap-2">
              {promptChips.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={onStartCall}
                  className="rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-3.5 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-200 shadow-sm hover:border-[#0F4C81] hover:text-[#0F4C81] transition-all hover:shadow-md cursor-pointer"
                >
                  💬 &quot;{prompt}&quot;
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Feature Cards Grid */}
        <section id="services" className="py-10 border-t border-slate-200/80 dark:border-slate-800">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">
              Core Citizen Assistance Services
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Comprehensive AI guidance designed for every Indian citizen
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {featureCards.map((card) => (
              <div
                key={card.id}
                className={`bg-white dark:bg-slate-800/90 p-6 rounded-2xl shadow-md border border-slate-200/60 dark:border-slate-700/60 hover:shadow-lg transition-all ${card.color} group`}
              >
                <div className="flex items-start justify-between">
                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-700/50 group-hover:scale-110 transition-transform">
                    {card.icon}
                  </div>
                  <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                    {card.badge}
                  </span>
                </div>
                <h3 className="mt-4 text-lg font-bold text-slate-900 dark:text-white group-hover:text-[#0F4C81] transition-colors">
                  {card.title}
                </h3>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
                  {card.desc}
                </p>
                <button
                  onClick={onStartCall}
                  className="mt-4 inline-flex items-center gap-1.5 text-xs font-bold text-[#0F4C81] dark:text-blue-400 hover:underline"
                >
                  Ask Voice AI <ArrowRightIcon size={14} />
                </button>
              </div>
            ))}
          </div>
        </section>

        {/* Trust Badges */}
        <section id="safety-tips" className="py-6 my-4 bg-white dark:bg-slate-800 rounded-2xl border border-slate-200 dark:border-slate-700 p-6 shadow-sm">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="flex flex-col items-center p-2">
              <ShieldCheckIcon size={28} className="text-[#0F4C81] dark:text-blue-400 mb-1" />
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Secure AI Assistance</span>
              <span className="text-[10px] text-slate-500">Official Standard</span>
            </div>
            <div className="flex flex-col items-center p-2">
              <LockKeyIcon size={28} className="text-[#2E7D32] dark:text-emerald-400 mb-1" />
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Privacy Protected</span>
              <span className="text-[10px] text-slate-500">Encrypted Audio</span>
            </div>
            <div className="flex flex-col items-center p-2">
              <BankIcon size={28} className="text-[#FF9933] dark:text-amber-400 mb-1" />
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Trusted Information</span>
              <span className="text-[10px] text-slate-500">Verified Welfare Data</span>
            </div>
            <div className="flex flex-col items-center p-2">
              <HeadsetIcon size={28} className="text-[#0F4C81] dark:text-blue-400 mb-1" />
              <span className="text-xs font-bold text-slate-800 dark:text-slate-200">Multilingual Support</span>
              <span className="text-[10px] text-slate-500">Voice-First Portal</span>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer id="contact" className="text-center py-4 border-t border-slate-200/60 dark:border-slate-800 text-xs text-slate-500">
          <p className="font-medium">
            🛡️ <strong>Jan Sahay (जन सहाय)</strong> — AI Citizen Assistance Platform for Financial Literacy, Cyber Safety & Public Welfare.
          </p>
          <p className="mt-1 text-[11px] text-slate-400">
            For emergency cyber fraud reporting, call National Cyber Crime Helpline: <strong>1930</strong>.
          </p>
        </footer>
      </div>
    );
  }
);

WelcomeView.displayName = 'WelcomeView';

