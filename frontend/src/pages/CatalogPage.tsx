import React, { useEffect, useState } from 'react';
import { api, ApiException } from '../api/client';
import { ProductCard } from '../components/ProductCard';
import { ApiError, Product } from '../types';

interface CatalogPageProps {
  onAddToCart: (product: Product, quantity: number) => void;
  onError: (error: ApiError | null) => void;
}

export const CatalogPage: React.FC<CatalogPageProps> = ({ onAddToCart, onError }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const fetchCatalog = async (search?: string) => {
    setLoading(true);
    onError(null);
    try {
      const data = await api.getProducts(search);
      setProducts(data.items);
    } catch (err) {
      if (err instanceof ApiException) {
        onError(err.errorData);
      } else {
        onError({
          code: 'CLIENT_ERROR',
          message: 'An unexpected client error occurred',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCatalog();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCatalog(searchTerm);
  };

  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1.5rem',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>
            Product Catalog
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
            Served by <code>product-service</code> via <code>api-gateway</code>
          </p>
        </div>

        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '0.5rem' }}>
          <input
            type="text"
            placeholder="Search products..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              padding: '0.5rem 0.85rem',
              border: '1px solid #cbd5e1',
              borderRadius: '6px',
              fontSize: '0.9rem',
              minWidth: '220px',
            }}
          />
          <button
            type="submit"
            style={{
              backgroundColor: '#0284c7',
              color: '#ffffff',
              border: 'none',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Search
          </button>
          <button
            type="button"
            onClick={() => {
              setSearchTerm('');
              fetchCatalog();
            }}
            style={{
              backgroundColor: '#f1f5f9',
              color: '#475569',
              border: '1px solid #cbd5e1',
              padding: '0.5rem 0.85rem',
              borderRadius: '6px',
              cursor: 'pointer',
            }}
          >
            Reset
          </button>
        </form>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
          ⏳ Loading catalog items...
        </div>
      ) : products.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '3rem',
          backgroundColor: '#ffffff',
          borderRadius: '8px',
          border: '1px solid #e2e8f0',
        }}>
          <p style={{ color: '#64748b', fontSize: '1rem' }}>No products found matching your query.</p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
          gap: '1.25rem',
        }}>
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAddToCart={onAddToCart}
            />
          ))}
        </div>
      )}
    </div>
  );
};
