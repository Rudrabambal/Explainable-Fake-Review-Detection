import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Analyze from './components/Analyze';

export default function App() {
  // Always true for the new tech aesthetic
  const [darkMode, setDarkMode] = useState(true);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  return (
    <div className="dark">
      <div className="min-h-screen bg-[#09090b] text-zinc-100 font-sans selection:bg-emerald-500/30 selection:text-emerald-400 cyber-grid relative overflow-hidden">

        {/* Glow Background Elements */}
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none"></div>

        {/* Top Navbar */}
        <Navbar darkMode={darkMode} toggleDarkMode={toggleDarkMode} />

        <main className="relative z-10 p-4 md:p-8">
          <div className="max-w-6xl mx-auto flex flex-col items-center">


            {/* High-Impact Hero Section */}
            <section className="w-full text-left py-20 animate-fade-up">
              <div className="flex items-center space-x-2 mb-8">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                <span className="text-emerald-500 text-xs font-bold tracking-[0.2em] uppercase">AI Detection Engine v2.4</span>
                <span className="text-zinc-600 text-xs font-medium border-l border-zinc-800 pl-3">98.4% Accuracy - 2.1s Avg Detection</span>
              </div>

              <h1 className="text-7xl md:text-9xl font-black tracking-tighter leading-[0.8] mb-10">
                SPOT<br />
                <span className="text-emerald-500 glow-text">FAKE</span><br />
                REVIEWS.
              </h1>

              <p className="max-w-xl text-zinc-400 text-xl leading-relaxed mb-12">
                Machine-learning model trained on 50M+ reviews. Detects manipulation patterns, synthetic text, and coordinated fraud — in under 3 seconds.
              </p>

              <div className="flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-6">
                <button
                  onClick={() => document.getElementById('analyze-section').scrollIntoView({ behavior: 'smooth' })}
                  className="w-full sm:w-auto bg-emerald-500 hover:bg-emerald-400 text-black font-bold px-10 py-5 rounded-full shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all flex items-center justify-center group"
                >
                  Analyze a Review Free
                  <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 8l4 4m0 0l-4 4m4-4H3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                </button>
                <button className="w-full sm:w-auto flex items-center justify-center space-x-3 px-10 py-5 rounded-full border border-zinc-800 hover:bg-zinc-900 transition-all text-zinc-300 font-bold">
                  <div className="w-8 h-8 rounded-full border border-zinc-700 flex items-center justify-center text-xs">▶</div>
                  <span>See How It Works</span>
                </button>
              </div>
            </section>

            {/* Analysis Tool Section */}
            <div id="analyze-section" className="w-full pt-20">
              <Analyze />
            </div>

          </div>
        </main>

        <footer className="py-12 text-center text-zinc-600 text-xs border-t border-zinc-900 mt-20 relative z-10">
          <div className="max-w-6xl mx-auto px-8 flex flex-col md:flex-row items-center justify-between">
            <div>© 2026 FakeReviewDetect AI. All rights reserved. MADE BY RUDRA & VIPLAV.</div>
            <div className="flex space-x-8 mt-4 md:mt-0">
              <a href="#" className="hover:text-zinc-400 transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-zinc-400 transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-zinc-400 transition-colors">Documentation</a>
            </div>
          </div>
        </footer>

      </div>
    </div>
  );
}
