import React, { useState, useEffect } from 'react';

const CATEGORIES = [
  { id: 'hotel', name: 'Hotel', icon: '🏨', placeholder: '“Stayed here for 2 nights and honestly had a pretty comfortable experience. The room was clean, the bed was soft, and housekeeping was consistent. The only minor issue was the WiFi being a bit slow during peak hours, but overall it didn’t affect my stay much. Would consider coming back.”..' },
  { id: 'product', name: 'Product', icon: '📦', placeholder: '“This product exceeded all my expectations! The build quality is premium, and it performs exactly as described. I’ve been using it for a week now, and I haven’t found a single flaw. Worth every penny.”' },
  { id: 'movie', name: 'Movie', icon: '🎬', placeholder: '“Went in with low expectations but was pleasantly surprised. The storyline was engaging, and the performances felt genuine. The second half was stronger than the first. Definitely worth watching once.”' },
  { id: 'restaurant', name: 'Restaurant', icon: '🍽️', placeholder: '“The food was absolutely delicious and the service was top-notch. Every dish we tried was flavorful and well-prepared. The ambiance was great too. Highly recommend this place!”' },
];

export default function Analyze() {
  const [category, setCategory] = useState(null);
  const [reviewText, setReviewText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!reviewText.trim()) return;

    setIsAnalyzing(true);
    setResult(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ review: reviewText, category }),
      });

      const data = await response.json();

      if (data.success) {
        setResult({
          status: data.prediction,
          confidence: data.confidence,
          sentiment: data.sentiment,
          emotion: data.emotion,
          type: data.type,
          explanation: data.explanation,
          base_value: data.base_value
        });
      } else {
        alert("Server Error: " + data.error);
      }
    } catch (error) {
      console.error("Analysis failed:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetForm = () => {
    setCategory(null);
    setReviewText('');
    setResult(null);
  };

  if (!category) {
    return (
      <div className="w-full max-w-4xl text-center py-20 animate-fade-up">
        <h2 className="text-4xl font-black mb-4 tracking-tight text-white">
          What are we auditing today?
        </h2>
        <p className="text-zinc-500 mb-12 text-lg">
          Select a category to begin your high-fidelity fraud detection scan.
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setCategory(cat.id)}
              className="glass-morphism p-8 rounded-[2rem] hover:border-emerald-500/50 hover:shadow-[0_0_30px_rgba(16,185,129,0.1)] transition-all duration-300 group"
            >
              <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">{cat.icon}</div>
              <span className="font-bold text-zinc-300 group-hover:text-emerald-400 transition-colors uppercase tracking-widest text-xs">{cat.name}</span>
            </button>
          ))}
        </div>
      </div>
    );
  }

  const activeCategory = CATEGORIES.find(c => c.id === category);

  return (
    <div className="w-full max-w-6xl space-y-12 animate-fade-up">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={resetForm}
            className="w-12 h-12 rounded-full glass-morphism flex items-center justify-center hover:bg-zinc-800 transition-colors"
          >
            <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 19l-7-7 7-7" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </button>
          <div>
            <h2 className="text-3xl font-black flex items-center text-white italic">
              <span className="mr-3 opacity-50">/</span>
              {activeCategory.name.toUpperCase()} SCAN
            </h2>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        {/* Input Area */}
        <div className="lg:col-span-12">
          <div className="glass-morphism rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
            <textarea
              rows="6"
              className="w-full rounded-2xl border-0 bg-zinc-900/50 p-8 text-xl text-zinc-100 placeholder:text-zinc-700 focus:ring-1 focus:ring-emerald-500/50 transition-all resize-none outline-none"
              placeholder={activeCategory.placeholder}
              value={reviewText}
              onChange={(e) => setReviewText(e.target.value)}
            ></textarea>

            <div className="mt-8 flex justify-end">
              <button
                onClick={handleAnalyze}
                disabled={!reviewText.trim() || isAnalyzing}
                className={`px-12 py-5 rounded-full font-black text-lg transition-all duration-300 flex items-center space-x-4 ${!reviewText.trim() || isAnalyzing
                    ? 'bg-zinc-800 text-zinc-600 cursor-not-allowed'
                    : 'bg-emerald-500 hover:bg-emerald-400 text-black shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:scale-[1.02]'
                  }`}
              >
                {isAnalyzing ? (
                  <>
                    <svg className="animate-spin h-6 w-6 text-black" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>AUDITING...</span>
                  </>
                ) : (
                  <>
                    <span>RUN AUTHENTICITY SCAN</span>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {result && (
          <>
            {/* Verdict Card */}
            <div className="lg:col-span-4">
              <div className={`glass-morphism rounded-[2.5rem] p-10 h-full border-2 ${result.status === 'Fake' ? 'border-red-500/20' : 'border-emerald-500/20'
                }`}>
                <div className={`text-xs font-black uppercase tracking-[0.3em] mb-4 text-center ${result.status === 'Fake' ? 'text-red-500' : 'text-emerald-500'
                  }`}>
                  Neural Integrity Result
                </div>
                <div className="text-7xl font-black text-center mb-6 tracking-tighter text-white">
                  {result.status.toUpperCase()}
                </div>
                <div className="space-y-6">
                  <div className="bg-zinc-900/50 rounded-2xl p-6 text-center">
                    <div className="text-zinc-600 font-bold uppercase tracking-widest text-[10px] mb-2">Confidence Level</div>
                    <div className="text-4xl font-black text-white">{result.confidence.toFixed(1)}<span className="text-lg opacity-30">%</span></div>
                    <div className="w-full bg-zinc-800 h-1.5 rounded-full mt-4 overflow-hidden">
                      <div
                        className={`h-full transition-all duration-1000 ${result.status === 'Fake' ? 'bg-red-500' : 'bg-emerald-500'}`}
                        style={{ width: `${result.confidence}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="glass-morphism rounded-2xl p-4 text-center">
                      <div className="text-[9px] font-bold text-zinc-600 uppercase mb-1">Sentiment</div>
                      <div className="text-sm font-black text-zinc-100">{result.sentiment}</div>
                    </div>
                    <div className="glass-morphism rounded-2xl p-4 text-center">
                      <div className="text-[9px] font-bold text-zinc-600 uppercase mb-1">Emotion</div>
                      <div className="text-sm font-black text-zinc-100">{result.emotion}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Explanation Card */}
            <div className="lg:col-span-8 animate-fade-up" style={{ animationDelay: '0.2s' }}>
              <div className="glass-morphism rounded-[2.5rem] p-10 h-full relative overflow-hidden">
                <div className="flex items-center justify-between mb-8">
                  <h3 className="text-xl font-bold flex items-center text-white">
                    <svg className="w-6 h-6 mr-3 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                    Neural Activation Model
                  </h3>
                  <div className="px-4 py-1 rounded-full border border-zinc-800 text-[10px] font-black tracking-widest text-zinc-500 uppercase">
                    Feature Attribution Map
                  </div>
                </div>

                <div className="p-8 rounded-3xl bg-zinc-900/50 text-zinc-100 leading-relaxed text-xl whitespace-pre-wrap font-medium">
                  {result.explanation.map(([token, score], index) => {
                    let style = {};
                    if (score > 0.005) {
                      const opacity = Math.min(Math.max(score * 2, 0.1), 0.8);
                      style = { backgroundColor: `rgba(239, 68, 68, ${opacity})`, color: 'white' };
                    } else if (score < -0.005) {
                      const opacity = Math.min(Math.max(Math.abs(score) * 2, 0.1), 0.8);
                      style = { backgroundColor: `rgba(16, 185, 129, ${opacity})`, color: 'white' };
                    }
                    return (
                      <span key={index} className="inline px-1 rounded transition-all" style={style}>
                        {token}
                      </span>
                    );
                  })}
                </div>

                <div className="mt-8 flex items-center space-x-6">
                  <div className="flex items-center text-[10px] space-x-2">
                    <div className="w-3 h-3 rounded bg-emerald-500"></div>
                    <span className="text-zinc-500 font-bold uppercase tracking-widest">Evidence for Authentic</span>
                  </div>
                  <div className="flex items-center text-[10px] space-x-2">
                    <div className="w-3 h-3 rounded bg-red-500"></div>
                    <span className="text-zinc-500 font-bold uppercase tracking-widest">Evidence for Fake</span>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
