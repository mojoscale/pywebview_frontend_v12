// src/types/index.ts
export interface Project {
  project_id: string;
  name: string;
  board: string;
  description?: string; // Make it optional
  is_active: boolean;
  updated_at: string;
  created_at: string;
  project_type?: string;
  metadata?: any;
}

export interface Board {
  id: string;
  name: string;
  fqbn: string;
}

export interface EnvVariable {
  key: string;
  value: string;
  description?: string;
  is_secret?: boolean;
}

export interface CompileStatus {
  completed: boolean;
  success: boolean;
  error?: string;
  warnings?: string[];
  suggestions?: string[];
  specs?: any;
  status?: string;
  message?: string;
}

export interface CompletionItem {
  label: string;
  kind: number;
  detail?: string;
  documentation?: string;
  insertText?: string; // Add this missing property
}


export interface SerialStatus {
  available: boolean;
  ip?: string;
}



export interface CompilationResult {
  success: boolean;
  error?: string;
  warnings: string[];
  suggestions: string[];
  message?: string; // Add this
  timestamp?: string; // Add this
  fileName?: string;
  specs: {
    flash: {
      used: number;
      total: number;
    };
    ram: {
      used: number;
      total: number;
    };
    additional?: {
      [key: string]: string;
    };
  };
}