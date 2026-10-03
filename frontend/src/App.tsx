import React, { useState } from 'react';
import { ErrorBanner } from './components/ErrorBanner';
import { Navbar } from './components/Navbar';
import { CatalogPage } from './pages/CatalogPage';
import { CartItem, CheckoutModal } from './pages/CheckoutModal';
import { OrdersPage } from './pages/OrdersPage';
import { ApiError, Product } from './types';

export const App: React.FC = () => {
  const [currentTab, setCurrentTab] = useState<'catalog' | 'orders'>('catalog');
  const [cart, setCart] = useState<CartItem[]>([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleAddToCart = (product: Product, quantity: number) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.product.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + quantity }
            : item
        );
      }
      return [...prev, { product, quantity }];
    });
    setSuccessMessage(`Added ${quantity} × "${product.name}" to cart.`);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  const handleUpdateQuantity = (productId: number, quantity: number) => {
    if (quantity <= 0) {
      setCart((prev) => prev.filter((item) => item.product.id !== productId));
    } else {
      setCart((prev) =>
        prev.map((item) => (item.product.id === productId ? { ...item, quantity } : item))
      );
    }
  };

  const handleClearCart = () => setCart([]);

  const handleOrderSuccess = (orderId: number) => {
    setSuccessMessage(`Order #${orderId} was successfully placed!`);
    setCurrentTab('orders');
    setTimeout(() => setSuccessMessage(null), 5000);
  };

  const totalCartCount = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        cartCount={totalCartCount}
        onOpenCart={() => setIsCartOpen(true)}
      />

      <main style={{ maxWidth: '1100px', width: '100%', margin: '0 auto', padding: '1.5rem 1rem', flex: 1 }}>
        {/* Success Alert */}
        {successMessage && (
          <div style={{
            backgroundColor: '#ecfdf5',
            borderLeft: '4px solid #10b981',
            padding: '0.85rem 1.25rem',
            borderRadius: '6px',
            marginBottom: '1.5rem',
            color: '#065f46',
            fontWeight: 600,
          }}>
            ✅ {successMessage}
          </div>
        )}

        {/* Microservice Failure Banner */}
        <ErrorBanner error={error} onDismiss={() => setError(null)} />

        {currentTab === 'catalog' ? (
          <CatalogPage onAddToCart={handleAddToCart} onError={setError} />
        ) : (
          <OrdersPage onError={setError} />
        )}
      </main>

      <footer style={{
        backgroundColor: '#f1f5f9',
        borderTop: '1px solid #e2e8f0',
        padding: '1.25rem 2rem',
        textAlign: 'center',
        fontSize: '0.85rem',
        color: '#64748b',
      }}>
        KubeShop Cloud-Native Architecture &bull; Frontend &rarr; API Gateway (8000) &rarr; Product Service (8001) &bull; Order Service (8002)
      </footer>

      <CheckoutModal
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        cart={cart}
        onUpdateQuantity={handleUpdateQuantity}
        onClearCart={handleClearCart}
        onOrderSuccess={handleOrderSuccess}
        onError={setError}
      />
    </div>
  );
};

export default App;
