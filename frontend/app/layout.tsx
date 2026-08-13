import { Public_Sans } from 'next/font/google';
import localFont from 'next/font/local';
import { headers } from 'next/headers';
import { ThemeProvider } from '@/components/app/theme-provider';
import { ThemeToggle } from '@/components/app/theme-toggle';
import { cn } from '@/lib/shadcn/utils';
import { getAppConfig, getStyles } from '@/lib/utils';
import '@/styles/globals.css';

const publicSans = Public_Sans({
  variable: '--font-public-sans',
  subsets: ['latin'],
});

const commitMono = localFont({
  display: 'swap',
  variable: '--font-commit-mono',
  src: [
    {
      path: '../fonts/CommitMono-400-Regular.otf',
      weight: '400',
      style: 'normal',
    },
    {
      path: '../fonts/CommitMono-700-Regular.otf',
      weight: '700',
      style: 'normal',
    },
    {
      path: '../fonts/CommitMono-400-Italic.otf',
      weight: '400',
      style: 'italic',
    },
    {
      path: '../fonts/CommitMono-700-Italic.otf',
      weight: '700',
      style: 'italic',
    },
  ],
});

interface RootLayoutProps {
  children: React.ReactNode;
}

export default async function RootLayout({ children }: RootLayoutProps) {
  const hdrs = await headers();
  const appConfig = await getAppConfig(hdrs);
  const styles = getStyles(appConfig);
  const { pageTitle, pageDescription, companyName, logo, logoDark } = appConfig;

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn(
        publicSans.variable,
        commitMono.variable,
        'scroll-smooth font-sans antialiased'
      )}
    >
      <head>
        {styles && <style>{styles}</style>}
        <title>{pageTitle}</title>
        <meta name="description" content={pageDescription} />
      </head>
      <body className="overflow-x-hidden bg-[#F8FAFC] dark:bg-[#0B132B]">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {/* Subtle Tricolor Top Strip */}
          <div className="jan-tricolor-strip h-1.5 w-full fixed top-0 left-0 z-[60]" />

          {/* Navigation Header */}
          <header className="fixed top-1.5 left-0 z-50 w-full bg-white/90 backdrop-blur-md border-b border-slate-200/80 dark:bg-slate-900/90 dark:border-slate-800">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
              <a href="#" className="flex items-center gap-2.5 group">
                <div className="flex size-9 items-center justify-center rounded-xl bg-[#0F4C81] text-white font-bold shadow-md shadow-[#0F4C81]/30 transition-transform group-hover:scale-105">
                  🛡️
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-lg leading-none tracking-tight text-[#0F4C81] dark:text-blue-400">
                    Jan Sahay
                  </span>
                  <span className="text-[10px] font-medium tracking-wide text-emerald-700 dark:text-emerald-400">
                    जन सहाय • Citizen AI Portal
                  </span>
                </div>
              </a>

              {/* Nav Links */}
              <nav className="hidden items-center gap-6 md:flex text-sm font-semibold text-slate-700 dark:text-slate-200">
                <a href="/" className="hover:text-[#0F4C81] transition-colors">Home</a>
                <a href="/analytics" className="hover:text-[#0F4C81] transition-colors flex items-center gap-1">Analytics 📊</a>
                <a href="/escalations" className="hover:text-[#0F4C81] transition-colors flex items-center gap-1">Escalations 🚨</a>
                <a href="/#services" className="hover:text-[#0F4C81] transition-colors">Services</a>
                <a href="/#safety-tips" className="hover:text-[#0F4C81] transition-colors">Safety Tips</a>
              </nav>

              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800">
                  <span className="size-2 rounded-full bg-emerald-500 animate-pulse" />
                  Live AI Assistance
                </span>
              </div>
            </div>
          </header>

          <div className="pt-16">
            {children}
          </div>

          <div className="group fixed bottom-2 right-4 z-50">
            <ThemeToggle className="shadow-lg" />
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
