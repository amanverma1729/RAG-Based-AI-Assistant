import React from 'react';
import { Plus, User, X } from 'lucide-react';

export default function Sidebar({ isOpen, setIsOpen }) {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <div className={`fixed inset-y-0 left-0 z-50 w-[260px] bg-surface-sidebar flex flex-col transform transition-transform duration-300 ease-in-out md:relative md:translate-x-0 shrink-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        
        {/* Mobile Close Button (Outside Sidebar) */}
        {isOpen && (
          <button 
            onClick={() => setIsOpen(false)}
            className="md:hidden absolute -right-12 top-4 p-2 text-white hover:bg-white/10 rounded-md"
          >
            <X size={24} />
          </button>
        )}

        <div className="p-3">
          <button className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-surface-hover transition-colors text-text-primary text-sm font-medium">
            <div className="w-7 h-7 rounded-full bg-surface-base flex items-center justify-center border border-border-active shrink-0">
              <Plus size={16} />
            </div>
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-2">
          <div className="mb-6">
            <h3 className="text-xs font-semibold text-text-tertiary mb-3 px-3">Today</h3>
            <ul className="space-y-1">
              <li>
                <button className="w-full text-left px-3 py-2 text-sm text-text-primary bg-surface-card rounded-lg hover:bg-surface-hover transition-colors truncate">
                  RAG Assistant Architecture
                </button>
              </li>
              <li>
                <button className="w-full text-left px-3 py-2 text-sm text-text-secondary hover:bg-surface-hover rounded-lg transition-colors truncate">
                  AWS Deployment Steps
                </button>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-xs font-semibold text-text-tertiary mb-3 px-3">Previous 7 Days</h3>
            <ul className="space-y-1">
              {[
                "Python Script Debugging",
                "React Context vs Redux",
                "Database Schema Review",
                "REST API Authentication"
              ].map((chat, i) => (
                <li key={i}>
                  <button className="w-full text-left px-3 py-2 text-sm text-text-secondary hover:bg-surface-hover rounded-lg transition-colors truncate">
                    {chat}
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="p-3 border-t border-border-active/30 mt-auto">
          <button className="flex items-center gap-3 w-full p-3 rounded-lg hover:bg-surface-hover transition-colors text-text-primary text-sm font-medium">
            <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-accent-emerald to-green-600 flex items-center justify-center text-white shrink-0">
              <User size={14} />
            </div>
            User Profile
          </button>
        </div>
      </div>
    </>
  );
}
