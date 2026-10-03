import React, { useState } from 'react';
import { Product } from '../types';

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product, quantity: number) => void;
}

export const ProductCard: React.FC<ProductCardProps> = ({ product, onAddToCart }) => {
  const [quantity, setQuantity] = useState(1);
  const isOutOfStock = product.stock <= 0;

  return (
    <div style={{
      backgroundColor: '#ffffff',
      border: '1px solid #e2e8f0',
      borderRadius: '8px',
      padding: '1.25rem',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
      transition: 'box-shadow 0.2s',
    }}>
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>
            {product.name}
          </h3>
          <span style={{
            fontSize: '1.1rem',
            fontWeight: 700,
            color: '#0369a1',
          }}>
            ${Number(product.price).toFixed(2)}
          </span>
        </div>
        <p style={{
          color: '#64748b',
          fontSize: '0.875rem',
          marginBottom: '1rem',
          lineHeight: '1.4',
        }}>
          {product.description || 'No description available.'}
        </p>
      </div>

      <div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '0.85rem',
          fontSize: '0.85rem',
        }}>
          <span style={{
            color: isOutOfStock ? '#ef4444' : '#10b981',
            fontWeight: 600,
          }}>
            {isOutOfStock ? '● Out of Stock' : `● ${product.stock} in stock`}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="number"
            min="1"
            max={Math.max(1, product.stock)}
            value={quantity}
            disabled={isOutOfStock}
            onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
            style={{
              width: '60px',
              padding: '0.4rem',
              border: '1px solid #cbd5e1',
              borderRadius: '4px',
              textAlign: 'center',
            }}
          />
          <button
            onClick={() => onAddToCart(product, quantity)}
            disabled={isOutOfStock}
            style={{
              flex: 1,
              backgroundColor: isOutOfStock ? '#cbd5e1' : '#0284c7',
              color: '#ffffff',
              border: 'none',
              padding: '0.5rem',
              borderRadius: '4px',
              fontWeight: 600,
              fontSize: '0.9rem',
              cursor: isOutOfStock ? 'not-allowed' : 'pointer',
            }}
          >
            {isOutOfStock ? 'Unavailable' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  );
};
