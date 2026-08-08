export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  audioVisualizerType?: 'bar' | 'wave' | 'grid' | 'radial' | 'aura';
  audioVisualizerColor?: `#${string}`;
  audioVisualizerColorDark?: `#${string}`;
  audioVisualizerColorShift?: number;
  audioVisualizerBarCount?: number;
  audioVisualizerGridRowCount?: number;
  audioVisualizerGridColumnCount?: number;
  audioVisualizerRadialBarCount?: number;
  audioVisualizerRadialRadius?: number;
  audioVisualizerWaveLineWidth?: number;

  // agent dispatch configuration
  agentName?: string;

  // LiveKit Cloud Sandbox configuration
  sandboxId?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Jan Sahay | जन सहाय',
  pageTitle: 'Jan Sahay — Citizen AI Assistant (जन सहाय)',
  pageDescription:
    'Get instant guidance on government schemes, financial literacy, fraud prevention, cyber safety, banking, and digital payments through secure AI voice conversations.',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/jan-sahay-avatar.png',
  accent: '#0F4C81',
  logoDark: '/jan-sahay-avatar.png',
  accentDark: '#FF9933',
  startButtonText: '🎙️ Start Voice Assistant',

  audioVisualizerType: 'wave',
  audioVisualizerColor: '#0F4C81',
  audioVisualizerColorDark: '#FF9933',

  // agent dispatch configuration
  agentName: process.env.AGENT_NAME ?? undefined,

  // LiveKit Cloud Sandbox configuration
  sandboxId: undefined,
};
