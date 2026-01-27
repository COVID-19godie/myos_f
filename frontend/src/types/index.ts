// API 相关类型
export interface ApiResponse<T> {
  count?: number
  next?: string | null
  previous?: string | null
  results?: T[]
  [key: string]: any
}

export interface DesktopItem {
  id: number
  title: string
  type: 'category' | 'resource'
  preview?: PreviewItem[]
  data: {
    kind?: string
    file?: string
    link?: string
    icon_class?: string
    [key: string]: any
  }
}

export interface PreviewItem {
  cover?: string
  [key: string]: any
}

export interface Category {
  id: string
  name: string
  icon?: string
}

// UI 相关类型
export interface WindowInstance {
  id: string
  title: string
  type: 'folder' | 'iframe' | 'app' | 'pdf' | 'image'
  content?: any
  zIndex: number
  isMinimized: boolean
  isMaximized: boolean
  x: number
  y: number
  width?: number
  height?: number
}

export interface Toast {
  id: number
  message: string
  title?: string
  type: 'success' | 'warning' | 'info' | 'error'
  duration?: number
}

export interface ContextMenuItem {
  label: string
  action: string
  icon?: string
}