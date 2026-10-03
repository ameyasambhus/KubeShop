import React from 'react';
import { ApiError } from '../types';

interface ErrorBannerProps {
  error: ApiError | null;
  onDismiss?: () => void;
}

export const ErrorBanner: React.FC<ErrorBannerProps> = ({ error, onDismiss }) => {
  if (!error) return null;

  return (
    <div style={{
      backgroundColor: '#fef2f2',
      borderLeft: '4px solid #ef4444',
      padding: '1rem 1.25rem',
      borderRadius: '6px',
      margin: '1.5rem 0',
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={{ fontSize: '1.2rem' }}>⚠️</span>
            <strong style={{ color: '#991b1b', fontSize: '1rem' }}>
              Service Incident Detected [{error.code}]
            </strong>
          </div>
          <p style={{ color: '#b91c1c', fontSize: '0.9rem', marginBottom: '0.5rem' }}>
            {error.message}
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', fontSize: '0.8rem', color: '#7f1d1d' }}>
            {error.dependency && (
              <span><strong>Failing Dependency:</strong> <code>{error.dependency}</code></span>
            )}
            {error.request_id && (
              <span><strong>Correlation ID:</strong> <code>{error.request_id}</code></span>
            )}
          </div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            style={{
              background: 'none',
              border: 'none',
              color: '#991b1b',
              fontWeight: 'bold',
              cursor: 'pointer',
              fontSize: '1.1rem',
            }}
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
};
