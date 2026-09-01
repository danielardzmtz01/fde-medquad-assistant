import React from 'react';
import { ExternalLink, BookOpen, ShieldCheck } from 'lucide-react';

export interface CitationItem {
  citation_id: string;
  title: string;
  source_url: string;
  snippet: string;
  relevance_score: number;
}

interface SourceViewerProps {
  citations: CitationItem[];
  selectedCitation: CitationItem | null;
  onSelectCitation: (citation: CitationItem) => void;
}

export const SourceViewer: React.FC<SourceViewerProps> = ({
  citations,
  selectedCitation,
  onSelectCitation,
}) => {
  return (
    <div className="h-full flex flex-col bg-white border-l border-slate-200">
      <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
        <div className="flex items-center space-x-2">
          <BookOpen className="w-5 h-5 text-blue-600" />
          <h2 className="font-semibold text-slate-800">NIH Grounding Sources</h2>
        </div>
        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">
          {citations.length} Verified
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {citations.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-sm">
            <BookOpen className="w-8 h-8 mx-auto mb-2 opacity-40" />
            No active literature sources loaded for current view.
          </div>
        ) : (
          citations.map((citation) => {
            const isSelected = selectedCitation?.citation_id === citation.citation_id;
            return (
              <div
                key={citation.citation_id}
                onClick={() => onSelectCitation(citation)}
                className={`p-3 rounded-lg border transition-all cursor-pointer ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50/50 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 bg-white'
                }`}
              >
                <div className="flex items-start justify-between">
                  <span className="font-mono text-xs font-bold text-blue-600 bg-blue-100 px-1.5 py-0.5 rounded">
                    {citation.citation_id}
                  </span>
                  <span className="text-xs text-slate-500 font-mono">
                    Score: {(citation.relevance_score * 100).toFixed(0)}%
                  </span>
                </div>
                <h3 className="text-sm font-medium text-slate-900 mt-2 line-clamp-2">
                  {citation.title}
                </h3>
                <p className="text-xs text-slate-600 mt-1 line-clamp-3">
                  {citation.snippet}
                </p>
                <a
                  href={citation.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center text-xs text-blue-600 hover:text-blue-800 mt-2 font-medium"
                  onClick={(e) => e.stopPropagation()}
                >
                  View Canonical NIH Document <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
