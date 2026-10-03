import React, { useState } from 'react';
import { api, ApiException } from '../api/client';
import { ApiError, Product } from '../types';

export interface CartItem {
  product: Product;
  quantity: number;
}

interface CheckoutModalProps {
  isOpen: boolean;
  onClose: () => void;
  cart: CartItem[];
  onUpdateQuantity: (productId: number, quantity: number) => void;
  onClearCart: () => void;
  onOrderSuccess: (orderId: number) => void;
  onError: (error: ApiError | null) => void;
}

export const CheckoutModal: React.FC<CheckoutModalProps> = ({
  isOpen,
  onClose,
  cart,
  onUpdateQuantity,
  onClearCart,
  onOrderSuccess,
  onError,
}) => {
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const total = cart.reduce((sum, item) => sum + Number(item.product.price) * item.quantity, 0);

  const handleCheckout = async () => {
    if (cart.length === 0) return;
    setSubmitting(true);
    onError(null);

    const payload = {
      items: cart.map((i) => ({
        product_id: i.product.id,
        quantity: i.quantity,
      })),
    };

    try {
      const order = await api.createOrder(payload);
      onClearCart();
      onClose();
      onOrderSuccess(order.id);
    } catch (err) {
      if (err instanceof ApiException) {
        onError(err.errorData);
      } else {
        onError({
          code: 'ORDER_SUBMISSION_FAILED',
          message: 'An unexpected error occurred during order submission',
        });
      }
      onClose();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '1rem',
    }}>
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        width: '100%',
        maxWidth: '520px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
      }}>
        <div style={{
          padding: '1.25rem',
          borderBottom: '1px solid #e2e8f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Your Shopping Cart</h3>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: '#64748b' }}
          >
            ✕
          </button>
        </div>

        <div style={{ padding: '1.25rem', overflowY: 'auto', flex: 1 }}>
          {cart.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#64748b', padding: '2rem 0' }}>Your cart is empty.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {cart.map((item) => (
                <div
                  key={item.product.id}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.75rem',
                    backgroundColor: '#f8fafc',
                    borderRadius: '6px',
                  }}
                >
                  <div>
                    <h4 style={{ fontSize: '0.95rem', fontWeight: 600 }}>{item.product.name}</h4>
                    <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
                      ${Number(item.product.price).toFixed(2)} each
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <input
                      type="number"
                      min="0"
                      max={item.product.stock}
                      value={item.quantity}
                      onChange={(e) => onUpdateQuantity(item.product.id, parseInt(e.target.value) || 0)}
                      style={{
                        width: '55px',
                        padding: '0.35rem',
                        border: '1px solid #cbd5e1',
                        borderRadius: '4px',
                        textAlign: 'center',
                      }}
                    />
                    <button
                      onClick={() => onUpdateQuantity(item.product.id, 0)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: '#ef4444',
                        cursor: 'pointer',
                        fontWeight: 'bold',
                        fontSize: '1rem',
                        padding: '0.25rem',
                      }}
                      title="Remove item"
                    >
                      🗑
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {cart.length > 0 && (
          <div style={{
            padding: '1.25rem',
            borderTop: '1px solid #e2e8f0',
            backgroundColor: '#f8fafc',
            borderBottomLeftRadius: '8px',
            borderBottomRightRadius: '8px',
          }}>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1rem',
              fontSize: '1.1rem',
            }}>
              <span style={{ fontWeight: 600, color: '#475569' }}>Total:</span>
              <span style={{ fontWeight: 800, color: '#0369a1', fontSize: '1.25rem' }}>
                ${total.toFixed(2)}
              </span>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button
                onClick={onClose}
                style={{
                  flex: 1,
                  padding: '0.6rem',
                  border: '1px solid #cbd5e1',
                  borderRadius: '6px',
                  backgroundColor: '#ffffff',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleCheckout}
                disabled={submitting}
                style={{
                  flex: 2,
                  padding: '0.6rem',
                  border: 'none',
                  borderRadius: '6px',
                  backgroundColor: submitting ? '#94a3b8' : '#0284c7',
                  color: '#ffffff',
                  fontWeight: 700,
                  cursor: submitting ? 'not-allowed' : 'pointer',
                }}
              >
                {submitting ? 'Submitting Order...' : 'Place Order Now'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
