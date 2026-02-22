import React, { useState } from 'react';
import { TerminalSquare, Copy, Download, X, ChevronsRight } from 'lucide-react';

export default function CodePreview({ code, isOpen, onToggle }) {
    const [copied, setCopied] = useState(false);

    if (!code) return null;

    const handleCopy = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleDownload = () => {
        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'model.py';
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className={`fixed right-6 top-24 bottom-6 w-[400px] z-40 transition-transform duration-300 ease-in-out ${isOpen ? 'translate-x-0' : 'translate-x-[110%]'}`}>
            <div className="glass-panel h-full flex flex-col overflow-hidden">
                {/* Header */}
                <div className="bg-slate-900/80 px-4 py-3 border-b border-slate-700/50 flex justify-between items-center">
                    <div className="flex items-center space-x-2 text-slate-300">
                        <TerminalSquare className="w-4 h-4" />
                        <span className="font-semibold text-sm">Python Script</span>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button onClick={handleCopy} className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors" title="Copy code">
                            <Copy className="w-4 h-4" />
                        </button>
                        <button onClick={handleDownload} className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors" title="Download .py">
                            <Download className="w-4 h-4" />
                        </button>
                        <button onClick={onToggle} className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors" title="Close Code">
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* Code Content */}
                <div className="flex-1 overflow-auto p-4 bg-[#0d1117]">
                    <pre className="text-xs font-mono text-slate-300 leading-relaxed whitespace-pre" style={{ tabSize: 4 }}>
                        <code>
                            {code.split('\n').map((line, i) => (
                                <div key={i} className="flex">
                                    <span className="select-none text-slate-600 w-8 inline-block shrink-0 mr-4 text-right">{i + 1}</span>
                                    <span className="flex-1 overflow-visible">{line}</span>
                                </div>
                            ))}
                        </code>
                    </pre>
                </div>
            </div>
        </div>
    );
}
