import React, { useState, useCallback, useRef } from 'react';
import TopNav from './components/TopNav';
import PromptInput from './components/PromptInput';
import HistoryPanel from './components/HistoryPanel';
import CodePreview from './components/CodePreview';
import Viewer3D from './components/Viewer3D';
import { History, Code2, AlertTriangle, PlayCircle } from 'lucide-react';

export default function App() {
  const [pipelineState, setPipelineState] = useState('idle'); // idle, generating, error, success
  const [stlUrl, setStlUrl] = useState(null);
  const [code, setCode] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');

  const [historyOpen, setHistoryOpen] = useState(false);
  const [codeOpen, setCodeOpen] = useState(false);
  const [wireframe, setWireframe] = useState(false);

  const abortControllerRef = useRef(null);

  const updateHistory = (prompt, status) => {
    try {
      const saved = localStorage.getItem('cad_copilot_history');
      const history = saved ? JSON.parse(saved) : [];
      history.unshift({ prompt, timestamp: new Date().toISOString(), status });
      if (history.length > 10) history.pop();
      localStorage.setItem('cad_copilot_history', JSON.stringify(history));
    } catch (e) { }
  };

  const handleGenerate = useCallback(async (prompt, isRefinement = false) => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    abortControllerRef.current = new AbortController();

    setPipelineState('generating');
    setErrorMsg('');
    setErrorMsg(null);
    setStlUrl(null);

    const endpoint = isRefinement ? '/api/refine' : '/api/generate';
    const body = isRefinement
      ? JSON.stringify({ original_code: code, instruction: prompt })
      : JSON.stringify({ prompt });

    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        signal: abortControllerRef.current.signal
      });

      const data = await res.json();

      if (!res.ok || data.status === 'error') {
        const msg = data.error ? `${data.error.message} (${data.error.details || ''})` : 'Unknown Generation Error';
        throw new Error(msg);
      }

      setStlUrl(data.stl_url);
      setCode(data.code);
      setPipelineState('success');
      updateHistory(prompt, 'success');

    } catch (err) {
      if (err.name !== 'AbortError') {
        setPipelineState('error');
        setErrorMsg(err.message || 'Failed to connect to backend.');
        updateHistory(prompt, 'error');
      }
    }
  }, [code]);

  return (
    <div className="h-screen w-screen flex flex-col bg-[#0f172a] overflow-hidden text-slate-200">
      <TopNav />

      <main className="flex-1 flex gap-6 p-4 pt-4 relative overflow-hidden">

        {/* Left Column: Flow & Controls */}
        <div className="w-[420px] shrink-0 flex flex-col h-full space-y-4 z-10">

          <div className="glass-panel p-5 flex flex-col items-center justify-center space-y-4 shadow-2xl relative overflow-hidden">
            {/* Progress Status Display */}
            {pipelineState === 'generating' ? (
              <div className="flex flex-col items-center py-4">
                <PlayCircle className="w-10 h-10 text-blue-500 animate-pulse mb-3" />
                <p className="text-blue-400 font-medium">Processing Parametric Prompt...</p>
                <div className="w-full bg-slate-800 rounded-full h-1.5 mt-4 overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full w-2/3 animate-pulse" />
                </div>
              </div>
            ) : pipelineState === 'error' ? (
              <div className="flex flex-col items-center py-4 w-full">
                <AlertTriangle className="w-10 h-10 text-red-500 mb-2" />
                <p className="text-red-400 font-semibold mb-1">Generation Failed</p>
                <div className="w-full bg-red-950/40 border border-red-900/50 p-3 rounded-lg text-xs font-mono text-red-300 break-words max-h-32 overflow-y-auto">
                  {errorMsg}
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center py-8 opacity-60">
                <code className="text-4xl font-light tracking-tighter text-slate-500">READY</code>
                <p className="text-xs text-slate-500 mt-2">Waiting for instructions</p>
              </div>
            )}
          </div>

          <PromptInput
            onGenerate={(p) => handleGenerate(p, false)}
            onRefine={(p) => handleGenerate(p, true)}
            isGenerating={pipelineState === 'generating'}
            currentCode={code}
          />

          <div className="mt-auto flex gap-3">
            <button
              onClick={() => setHistoryOpen(!historyOpen)}
              className="flex items-center justify-center gap-2 flex-1 p-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700 shadow-md text-sm font-medium transition-all"
            >
              <History className="w-4 h-4 text-blue-400" /> History
            </button>
            <button
              onClick={() => setCodeOpen(!codeOpen)}
              disabled={!code}
              className="flex items-center justify-center gap-2 flex-1 p-3 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-slate-700 shadow-md text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Code2 className="w-4 h-4 text-emerald-400" /> View Code
            </button>
          </div>
        </div>

        {/* Right Column: 3D Viewport */}
        <div className="flex-1 h-full min-w-0 z-0">
          <Viewer3D
            stlUrl={stlUrl}
            wireframe={wireframe}
            onToggleWireframe={() => setWireframe(!wireframe)}
          />
        </div>

      </main>

      {/* Slide-out Panels */}
      <HistoryPanel
        isOpen={historyOpen}
        onToggle={() => setHistoryOpen(!historyOpen)}
        onLoadPrompt={(p) => handleGenerate(p, false)}
      />
      <CodePreview
        isOpen={codeOpen}
        onToggle={() => setCodeOpen(!codeOpen)}
        code={code}
      />
    </div>
  );
}
