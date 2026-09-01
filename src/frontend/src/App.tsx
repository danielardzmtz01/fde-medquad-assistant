import React, { useState } from 'react';
import { Activity, ShieldCheck, Sparkles, BookOpen, Layers } from 'lucide-react';
import { ChatInterface, Message } from './components/ChatInterface';
import { SourceViewer, CitationItem } from './components/SourceViewer';
import { TelemetryBar } from './components/TelemetryBar';

export const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome-1',
      role: 'assistant',
      content:
        'Welcome to **MedQuAD Clinical Assistant**.\n\n' +
        'I am a multi-agent biomedical research platform grounded in verified NIH literature. ' +
        'I can assist you with disease classifications, symptoms, clinical guidelines, and ongoing trials with zero hallucination.\n\n' +
        '*Note: I operate under strict non-diagnostic research protocols.*',
      timestamp: new Date().toISOString(),
    },
  ]);

  const [isLoading, setIsLoading] = useState(false);
  const [citations, setCitations] = useState<CitationItem[]>([]);
  const [selectedCitation, setSelectedCitation] = useState<CitationItem | null>(null);
  const [telemetry, setTelemetry] = useState({
    promptTokens: 0,
    completionTokens: 0,
    cachedTokens: 0,
    estimatedCost: 0,
    latencyMs: 0,
    guardrailStatus: 'ACTIVE (Model Armor)',
  });

  const handleSendMessage = async (query: string) => {
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: `msg-${Date.now()}-res`,
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        guardrails: data.guardrails,
        timestamp: data.timestamp,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setCitations(data.citations || []);
      if (data.citations?.length > 0) {
        setSelectedCitation(data.citations[0]);
      }

      setTelemetry({
        promptTokens: data.tokens.prompt_tokens,
        completionTokens: data.tokens.completion_tokens,
        cachedTokens: data.tokens.cached_tokens,
        estimatedCost: data.tokens.estimated_cost_usd,
        latencyMs: data.latency_ms,
        guardrailStatus: data.guardrails.action_taken,
      });
    } catch (error) {
      console.error('Error fetching clinical response:', error);
      const errorMessage: Message = {
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: 'Error connecting to the clinical backend API. Please verify backend service status.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-100 overflow-hidden font-sans">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-3.5 flex items-center justify-between shadow-sm shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow">
            <Activity className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-slate-900 flex items-center space-x-2">
              <span>MedQuAD Clinical Assistant</span>
              <span className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded-md font-mono">
                GCP Capstone
              </span>
            </h1>
            <p className="text-xs text-slate-500">
              Grounded Multi-Agent NIH Literature Engine • Powered by Vertex AI & ADK
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-md font-medium">
            <ShieldCheck className="w-4 h-4" />
            <span>Scope Lock Active</span>
          </div>
          <div className="flex items-center space-x-1.5 bg-slate-100 text-slate-700 border border-slate-200 px-2.5 py-1 rounded-md font-medium">
            <Layers className="w-4 h-4 text-blue-600" />
            <span>ADK Multi-Agent</span>
          </div>
        </div>
      </header>

      {/* Main Split-Pane Workspace */}
      <div className="flex-1 flex flex-row overflow-hidden">
        {/* Left: Chat Pane (65%) */}
        <div className="w-2/3 h-full">
          <ChatInterface
            messages={messages}
            isLoading={isLoading}
            onSendMessage={handleSendMessage}
            onSelectCitation={(c) => setSelectedCitation(c)}
          />
        </div>

        {/* Right: Split-Pane NIH Source Inspector (35%) */}
        <div className="w-1/3 h-full">
          <SourceViewer
            citations={citations}
            selectedCitation={selectedCitation}
            onSelectCitation={(c) => setSelectedCitation(c)}
          />
        </div>
      </div>

      {/* Bottom Observability & Telemetry Bar */}
      <TelemetryBar {...telemetry} />
    </div>
  );
};

export default App;
