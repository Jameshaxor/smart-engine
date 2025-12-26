import React, { useState } from 'react';
import { Sparkles, ArrowRight, BookOpen, ShieldCheck, Zap, Globe, Cpu, RotateCcw } from 'lucide-react';

export default function App() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input }),
      });
      const data = await response.json();
      setResult(data.analysis);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0c] text-slate-200 font-sans selection:bg-violet-500/30 overflow-x-hidden">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] bg-violet-600/10 blur-[120px] rounded-full" />
        <div className="absolute top-[20%] -right-[10%] w-[30%] h-[30%] bg-blue-600/10 blur-[120px] rounded-full" />
      </div>

      <main className="relative z-10 max-w-2xl mx-auto px-6 pt-16 pb-24">
        {/* Header */}
        <header className="flex flex-col items-center mb-12 text-center">
          <div className="w-14 h-14 bg-gradient-to-tr from-violet-600 to-blue-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg shadow-violet-500/20">
            <Sparkles className="text-white" size={28} />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Smart Engine</h1>
          <p className="text-slate-400 text-sm max-w-xs">High-fidelity intelligence & synthesis.</p>
        </header>

        {/* Input Bar */}
        <div className="relative group mb-12">
          <div className="absolute -inset-1 bg-gradient-to-r from-violet-600 to-blue-500 rounded-2xl blur opacity-25 group-focus-within:opacity-50 transition duration-1000"></div>
          <div className="relative flex items-center bg-[#16161a] rounded-2xl border border-white/5 p-2 shadow-2xl">
            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
              placeholder="Paste a URL or ask anything..."
              className="flex-1 bg-transparent px-5 py-4 text-white placeholder:text-slate-600 focus:outline-none text-base"
            />
            <button 
              onClick={handleAnalyze}
              disabled={loading}
              className="bg-white text-black p-4 rounded-xl hover:bg-slate-200 transition-all disabled:opacity-50"
            >
              {loading ? <RotateCcw className="animate-spin" size={20} /> : <ArrowRight size={20} />}
            </button>
          </div>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="bg-[#16161a] border border-white/5 rounded-2xl p-8 shadow-xl">
              <div className="flex items-center gap-2 mb-4 text-violet-400">
                <BookOpen size={18} />
                <span className="text-xs font-bold uppercase tracking-[0.2em]">Synthesis</span>
              </div>
              <p className="text-slate-200 leading-relaxed text-lg">{result.summary}</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-[#16161a] border border-white/5 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-3 text-blue-400">
                  <ShieldCheck size={18} />
                  <span className="text-xs font-bold uppercase tracking-[0.2em]">Perspective</span>
                </div>
                <p className="text-slate-400 text-sm italic leading-relaxed">"{result.ghost_truth}"</p>
              </div>

              <div className="bg-[#16161a] border border-white/5 rounded-2xl p-6">
                <div className="flex items-center gap-2 mb-3 text-emerald-400">
                  <Globe size={18} />
                  <span className="text-xs font-bold uppercase tracking-[0.2em]">Context</span>
                </div>
                <p className="text-slate-400 text-sm leading-relaxed">{result.context}</p>
              </div>
            </div>

            <div className="bg-gradient-to-br from-violet-900/20 to-transparent border border-violet-500/20 rounded-2xl p-8 shadow-xl">
              <div className="flex items-center gap-2 mb-6 text-white">
                <Zap size={18} className="fill-current text-violet-400" />
                <span className="text-xs font-bold uppercase tracking-[0.2em]">Actionable Items</span>
              </div>
              <ul className="space-y-4">
                {result.actions.map((item, i) => (
                  <li key={i} className="flex gap-4 text-slate-300 text-sm">
                    <span className="text-violet-400 font-bold">{i + 1}.</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {loading && (
          <div className="space-y-6 animate-pulse">
            <div className="h-48 bg-white/5 rounded-2xl"></div>
            <div className="grid grid-cols-2 gap-4">
              <div className="h-32 bg-white/5 rounded-2xl"></div>
              <div className="h-32 bg-white/5 rounded-2xl"></div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
