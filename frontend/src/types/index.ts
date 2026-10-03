export interface Product {
  id: number;
  name: string;
  description: string | null;
  price: string | number;
  stock: number;
  created_at: string;
  updated_at: string;
}

export interface ProductListResponse {
  total: number;
  items: Product[];
}

export interface OrderItem {
  id: number;
  product_id: number;
  product_name: string;
  unit_price: string | number;
  quantity: number;
}

export interface Order {
  id: number;
  status: string;
  total: string | number;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface OrderListResponse {
  total: number;
  items: Order[];
}

export interface OrderCreateItem {
  product_id: number;
  quantity: number;
}

export interface OrderCreatePayload {
  items: OrderCreateItem[];
}

export interface ApiError {
  code: string;
  message: string;
  request_id?: string;
  dependency?: string;
  details?: Record<string, unknown>;
}
