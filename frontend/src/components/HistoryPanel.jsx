import React, { useState, useEffect } from 'react';
import { History, Trash2, Clock, ChevronRight } from 'lucide-react';

export default function HistoryPanel({ onLoadPrompt, onToggle, isOpen }) {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        const saved = localStorage.getItem('cad_copilot_history');
        if (saved) {
            try {
                setHistory(JSON.parse(saved));
            } catch (e) {
                console.error("Failed to parse history.");
            }
        }
    }, []);

    const clearHistory = () => {
        localStorage.removeItem('cad_copilot_history');
        setHistory([]);
    };

    return (
        <div className={`fixed left-0 top-24 bottom-6 w-[320px] transition-transform duration-300 ease-in-out z-40 ${isOpen ? 'translate-x-0' : '-translate-x-[110%]'}`}>
            <div className="glass-panel mx-4 h-full flex flex-col">
                <div className="p-4 border-b border-slate-700/50 flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                        <History className="w-5 h-5 text-blue-400" />
                        <h2 className="font-semibold text-slate-200">History</h2>
                    </div>
                    <button
                        onClick={clearHistory}
                        className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-slate-800 rounded transition-colors"
                        title="Clear History"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto p-2 space-y-2">
                    {history.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-2">
                            <Clock className="w-8 h-8 opacity-50" />
                            <p className="text-sm">No history yet.</p>
                        </div>
                    ) : (
                        history.map((item, idx) => (
                            <div
                                key={idx}
                                onClick={() => onLoadPrompt(item.prompt)}
                                className="group p-3 rounded-lg border border-transparent hover:border-slate-700 hover:bg-slate-800/50 cursor-pointer transition-all"
                            >
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-xs text-slate-500 font-medium">
                                        {new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                    <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                                </div>
                                <p className="text-sm text-slate-300 line-clamp-2">{item.prompt}</p>
                                {item.status === 'error' && <span className="text-[10px] text-red-400 mt-1 block">Failed</span>}
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
}
