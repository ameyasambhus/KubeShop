import React from 'react';

interface NavbarProps {
  currentTab: 'catalog' | 'orders';
  onSelectTab: (tab: 'catalog' | 'orders') => void;
  cartCount: number;
  onOpenCart: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, onSelectTab, cartCount, onOpenCart }) => {
  return (
    <header style={{
      backgroundColor: '#1e293b',
      color: '#ffffff',
      padding: '0.85rem 2rem',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span style={{ fontSize: '1.4rem', fontWeight: 700, letterSpacing: '-0.5px' }}>
          ☸️ Kube<span style={{ color: '#38bdf8' }}>Shop</span>
        </span>
        <span style={{
          fontSize: '0.75rem',
          backgroundColor: '#334155',
          color: '#94a3b8',
          padding: '2px 8px',
          borderRadius: '4px',
          textTransform: 'uppercase',
          fontWeight: 600,
        }}>
          Microservices Edition
        </span>
      </div>

      <nav style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
        <button
          onClick={() => onSelectTab('catalog')}
          style={{
            background: 'none',
            border: 'none',
            color: currentTab === 'catalog' ? '#38bdf8' : '#cbd5e1',
            fontWeight: currentTab === 'catalog' ? 600 : 400,
            cursor: 'pointer',
            fontSize: '0.95rem',
            borderBottom: currentTab === 'catalog' ? '2px solid #38bdf8' : '2px solid transparent',
            paddingBottom: '4px',
          }}
        >
          Catalog
        </button>
        <button
          onClick={() => onSelectTab('orders')}
          style={{
            background: 'none',
            border: 'none',
            color: currentTab === 'orders' ? '#38bdf8' : '#cbd5e1',
            fontWeight: currentTab === 'orders' ? 600 : 400,
            cursor: 'pointer',
            fontSize: '0.95rem',
            borderBottom: currentTab === 'orders' ? '2px solid #38bdf8' : '2px solid transparent',
            paddingBottom: '4px',
          }}
        >
          Orders
        </button>
        <button
          onClick={onOpenCart}
          style={{
            backgroundColor: '#0284c7',
            color: '#ffffff',
            border: 'none',
            padding: '0.45rem 1rem',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 600,
            fontSize: '0.9rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          🛒 Cart ({cartCount})
        </button>
      </nav>
    </header>
  );
};
