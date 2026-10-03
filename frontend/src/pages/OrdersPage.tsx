import React, { useEffect, useState } from 'react';
import { api, ApiException } from '../api/client';
import { ApiError, Order } from '../types';

interface OrdersPageProps {
  onError: (error: ApiError | null) => void;
}

export const OrdersPage: React.FC<OrdersPageProps> = ({ onError }) => {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchOrders = async () => {
    setLoading(true);
    onError(null);
    try {
      const data = await api.getOrders();
      setOrders(data.items);
    } catch (err) {
      if (err instanceof ApiException) {
        onError(err.errorData);
      } else {
        onError({
          code: 'CLIENT_ERROR',
          message: 'Failed to load order history',
        });
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '1.5rem',
      }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>
            Customer Orders
          </h2>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
            Managed by <code>order-service</code> with cross-service verification
          </p>
        </div>
        <button
          onClick={fetchOrders}
          style={{
            backgroundColor: '#0284c7',
            color: '#ffffff',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: 600,
          }}
        >
          🔄 Refresh
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
          ⏳ Loading orders...
        </div>
      ) : orders.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '3rem',
          backgroundColor: '#ffffff',
          borderRadius: '8px',
          border: '1px solid #e2e8f0',
        }}>
          <p style={{ color: '#64748b', fontSize: '1rem' }}>No orders placed yet.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {orders.map((order) => (
            <div
              key={order.id}
              style={{
                backgroundColor: '#ffffff',
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                padding: '1.25rem',
                boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderBottom: '1px solid #f1f5f9',
                paddingBottom: '0.75rem',
                marginBottom: '0.75rem',
                flexWrap: 'wrap',
                gap: '0.5rem',
              }}>
                <div>
                  <span style={{ fontWeight: 700, fontSize: '1.1rem', color: '#0f172a', marginRight: '0.75rem' }}>
                    Order #{order.id}
                  </span>
                  <span style={{
                    backgroundColor: '#dcfce7',
                    color: '#15803d',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                  }}>
                    {order.status}
                  </span>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
                  {new Date(order.created_at).toLocaleString()}
                </div>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <h4 style={{ fontSize: '0.85rem', textTransform: 'uppercase', color: '#94a3b8', marginBottom: '0.5rem' }}>
                  Items Purchased:
                </h4>
                <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
                  {order.items.map((item) => (
                    <li
                      key={item.id}
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: '0.35rem 0',
                        fontSize: '0.9rem',
                        borderBottom: '1px dashed #f1f5f9',
                      }}
                    >
                      <span>
                        {item.product_name} <strong style={{ color: '#64748b' }}>× {item.quantity}</strong>
                      </span>
                      <span style={{ fontWeight: 600 }}>
                        ${(Number(item.unit_price) * item.quantity).toFixed(2)}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <div style={{
                display: 'flex',
                justifyContent: 'flex-end',
                alignItems: 'baseline',
                gap: '0.5rem',
                fontSize: '1.1rem',
              }}>
                <span style={{ color: '#64748b', fontSize: '0.9rem' }}>Order Total:</span>
                <span style={{ fontWeight: 800, color: '#0369a1' }}>
                  ${Number(order.total).toFixed(2)}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
