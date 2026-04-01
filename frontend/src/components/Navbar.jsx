import React from 'react';

export default function Navbar() {
  return (
    <header className="h-20 flex items-center justify-between px-8 md:px-12 shrink-0 relative z-50">
      <div className="flex items-center space-x-2">
        <div className="w-10 h-10 bg-emerald-500 rounded-xl flex items-center justify-center shadow-[0_0_15px_rgba(16,185,129,0.4)]">
          <svg className="w-6 h-6 text-black" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 2.18l7 3.12v4.7c0 4.67-3.13 8.94-7 10.11-3.87-1.17-7-5.44-7-10.11v-4.7l7-3.12zM12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zm0 2c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3z" />
          </svg>
        </div>
        <span className="text-2xl font-black tracking-tighter">
          FakeReview<span className="text-emerald-500">Detect</span>
        </span>
      </div>

    </header>
  );
}
