import { ApiError, Order, OrderCreatePayload, OrderListResponse, Product, ProductListResponse } from '../types';

const BASE_URL = '/api';

class ApiException extends Error {
  errorData: ApiError;
  status: number;

  constructor(status: number, errorData: ApiError) {
    super(errorData.message);
    this.status = status;
    this.errorData = errorData;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});
  headers.set('Content-Type', 'application/json');

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });
  } catch (err) {
    throw new ApiException(503, {
      code: 'NETWORK_FAILURE',
      message: 'Failed to communicate with API Gateway. Please check network connectivity or pod state.',
      details: { original_error: String(err) },
    });
  }

  if (!response.ok) {
    let errorData: ApiError;
    try {
      const json = await response.json();
      errorData = json.error || {
        code: `HTTP_${response.status}`,
        message: json.detail || response.statusText,
      };
    } catch {
      errorData = {
        code: `HTTP_${response.status}`,
        message: await response.text() || response.statusText,
      };
    }
    throw new ApiException(response.status, errorData);
  }

  return response.json();
}

export const api = {
  getProducts: (search?: string): Promise<ProductListResponse> => {
    const query = search ? `?search=${encodeURIComponent(search)}` : '';
    return request<ProductListResponse>(`/products${query}`);
  },

  getProduct: (id: number): Promise<Product> => {
    return request<Product>(`/products/${id}`);
  },

  createOrder: (payload: OrderCreatePayload): Promise<Order> => {
    return request<Order>('/orders', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },

  getOrders: (): Promise<OrderListResponse> => {
    return request<OrderListResponse>('/orders');
  },

  getOrder: (id: number): Promise<Order> => {
    return request<Order>(`/orders/${id}`);
  },
};

export { ApiException };
