import React, { useState, useRef, useEffect } from 'react';
import { Send, Wand2, Loader2, X } from 'lucide-react';

export default function PromptInput({ onGenerate, isGenerating, onRefine, currentCode }) {
    const [prompt, setPrompt] = useState('');
    const [isRefining, setIsRefining] = useState(false);
    const textareaRef = useRef(null);

    const maxLength = 1000;

    // Auto-resize textarea
    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
        }
    }, [prompt]);

    const handleSubmit = () => {
        if (!prompt.trim() || isGenerating) return;

        if (isRefining && currentCode) {
            onRefine(prompt.trim());
        } else {
            onGenerate(prompt.trim());
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="glass-panel p-4 flex flex-col space-y-3">
            {currentCode && (
                <div className="flex justify-between items-center mb-1">
                    <label className="flex items-center space-x-2 text-sm text-slate-300 cursor-pointer">
                        <input
                            type="checkbox"
                            checked={isRefining}
                            onChange={() => setIsRefining(!isRefining)}
                            className="rounded bg-slate-900 border-slate-700 text-blue-500 focus:ring-blue-500 focus:ring-offset-slate-800"
                        />
                        <span>Refine existing model</span>
                    </label>
                </div>
            )}

            <div className="relative">
                <textarea
                    ref={textareaRef}
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value.slice(0, maxLength))}
                    onKeyDown={handleKeyDown}
                    disabled={isGenerating}
                    placeholder={isRefining ? "E.g., Make the hole 2mm wider..." : "E.g., Create a parametric gear with 12 teeth and a 5mm central hole..."}
                    className="glass-input p-4 pr-12 min-h-[60px] text-sm"
                />

                <button
                    onClick={handleSubmit}
                    disabled={!prompt.trim() || isGenerating}
                    className="absolute right-2 bottom-2 p-2 rounded-md bg-blue-600 hover:bg-blue-500 text-white disabled:bg-slate-700 disabled:text-slate-500 transition-colors"
                >
                    {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : (isRefining ? <Wand2 className="w-5 h-5" /> : <Send className="w-5 h-5" />)}
                </button>
            </div>

            <div className="flex justify-between items-center px-1">
                <span className="text-xs text-slate-500 flex items-center gap-1">
                    <kbd className="bg-slate-800 px-1 py-0.5 rounded border border-slate-700 font-mono">Ctrl</kbd> + <kbd className="bg-slate-800 px-1 py-0.5 rounded border border-slate-700 font-mono">Enter</kbd> to submit
                </span>
                <span className={`text-xs ${prompt.length >= maxLength ? 'text-red-400' : 'text-slate-500'}`}>
                    {prompt.length} / {maxLength}
                </span>
            </div>
        </div>
    );
}
