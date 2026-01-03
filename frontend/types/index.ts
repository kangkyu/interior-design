// Project types
export interface Project {
  id: string;
  name: string;
  status: 'in_progress' | 'finalized' | 'archived';
  created_at: string;
  updated_at: string;
  has_room_photo: boolean;
  current_version: number | null;
  message_count: number;
}

export interface ProjectDetail extends Project {
  room_analysis: RoomAnalysis | null;
  current_image_url: string | null;
  original_image_url: string | null;
}

// Room analysis
export interface FurnitureItem {
  type: string;
  color?: string;
  style?: string;
  position?: string;
}

export interface RoomColors {
  walls?: string;
  floor?: string;
  ceiling?: string;
}

export interface RoomAnalysis {
  room_type: string;
  furniture: FurnitureItem[];
  colors: RoomColors;
  lighting?: string;
  style?: string;
  features: string[];
  dimensions_estimate?: Record<string, string>;
}

// Chat types
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  image_url?: string;
  uploaded_image_url?: string;
  version_number?: number;
  created_at: string;
}

export interface ChatResponse {
  type: 'design' | 'clarification' | 'error';
  message: string;
  image_url?: string;
  version?: number;
  changes?: DesignChange[];
}

export interface DesignChange {
  element: string;
  action: string;
  value?: string;
  style?: string;
  position?: string;
}

// Design version
export interface DesignVersion {
  id: string;
  version_number: number;
  image_url: string;
  thumbnail_url?: string;
  changes?: Record<string, unknown>[];
  is_favorite: boolean;
  is_final: boolean;
  created_at: string;
}

// Image upload
export interface ImageUploadResponse {
  image_url: string;
  thumbnail_url?: string;
  analysis: RoomAnalysis;
  message: string;
}

// Export types
export type ExportFormat = 'pdf' | 'shopping_list' | 'colors' | 'json';

export interface PaintMatch {
  brand: string;
  name: string;
  code: string;
  hex: string;
}

export interface PaintSpec {
  element: string;
  hex: string;
  matches: PaintMatch[];
  finish?: string;
  coverage_sqft?: number;
  gallons_needed?: number;
}

export interface FurnitureSpec {
  item: string;
  style: string;
  color: string;
  material?: string;
  dimensions?: string;
  similar_products: Array<{
    store: string;
    product: string;
    price: string;
  }>;
  price_range?: string;
}

export interface BudgetEstimate {
  category: string;
  low: number;
  high: number;
}

export interface DesignSpecification {
  project_id: string;
  project_name: string;
  generated_at: string;
  before_image_url: string;
  after_image_url: string;
  summary_of_changes: string[];
  paint: PaintSpec[];
  flooring?: Record<string, unknown>;
  furniture: FurnitureSpec[];
  lighting?: Record<string, unknown>;
  decor: Record<string, unknown>[];
  budget: BudgetEstimate[];
  total_budget_low: number;
  total_budget_high: number;
}

// WebSocket message types
export interface WSMessage {
  type: 'status' | 'response' | 'error';
  status?: string;
  message?: string;
  image_url?: string;
  version?: number;
  response_type?: string;
}
