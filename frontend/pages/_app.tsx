import type { AppProps } from 'next/app'
import '../styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className="min-h-screen relative overflow-x-hidden">
      <div className="pointer-events-none absolute inset-0 bg-radial-fade" />
      <div className="absolute -z-10 inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.08),transparent_40%),radial-gradient(circle_at_80%_30%,rgba(16,185,129,0.08),transparent_40%),radial-gradient(circle_at_50%_80%,rgba(236,72,153,0.08),transparent_40%)] animate-gradient-x" />
      <Component {...pageProps} />
    </div>
  )
}


