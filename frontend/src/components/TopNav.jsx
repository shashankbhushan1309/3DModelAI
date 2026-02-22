import React, { useEffect, useState } from 'react';
import { Box, Server, Settings, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function TopNav() {
    const [status, setStatus] = useState('checking');

    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                setStatus(data.status);
            } catch (err) {
                setStatus('error');
            }
        };

        checkStatus();
        const interval = setInterval(checkStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <nav className="glass-panel mx-4 mt-4 px-6 py-4 flex justify-between items-center z-50 relative">
            <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
                    <Box className="text-white w-6 h-6" />
                </div>
                <div>
                    <h1 className="text-xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                        CAD Copilot
                    </h1>
                    <p className="text-xs text-slate-400 font-medium">AI-Powered Parametric Modeling</p>
                </div>
            </div>

            <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2 bg-slate-900/50 px-3 py-1.5 rounded-full border border-slate-700/50">
                    <Server className="w-4 h-4 text-slate-400" />
                    <span className="text-sm font-medium text-slate-300">System Status:</span>
                    {status === 'checking' && <div className="w-3 h-3 rounded-full bg-yellow-500 animate-pulse" />}
                    {status === 'ok' && <CheckCircle className="w-4 h-4 text-green-500" />}
                    {status === 'warning' && <AlertCircle className="w-4 h-4 text-yellow-500" />}
                    {status === 'error' && <XCircle className="w-4 h-4 text-red-500" />}
                </div>

                <button className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors">
                    <Settings className="w-5 h-5" />
                </button>
            </div>
        </nav>
    );
}
