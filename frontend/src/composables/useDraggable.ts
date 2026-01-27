import { ref, reactive, onMounted, onUnmounted, Ref } from 'vue'

interface Position {
  x: number
  y: number
}

interface DraggableOptions {
  // 是否可拖拽
  disabled?: boolean
  // 边界限制
  bounds?: 'parent' | 'viewport' | HTMLElement
  // 最小拖拽距离（避免误触）
  threshold?: number
  // 拖拽时的样式类
  draggingClass?: string
  // 是否点击穿透
  clickThrough?: boolean
}

/**
 * 通用拖拽Hook - 解决前端OS开发中的窗口拖拽核心问题
 * 避坑指南：
 * 1. 使用transform替代top/left避免重排重绘
 * 2. 正确处理鼠标事件的target判断
 * 3. 边界检测和约束
 * 4. 性能优化：防抖和requestAnimationFrame
 */
export function useDraggable(
  targetRef: Ref<HTMLElement | null>, 
  options: DraggableOptions = {}
) {
  const {
    disabled = false,
    bounds = 'viewport',
    threshold = 5,
    draggingClass = 'dragging',
    clickThrough = false
  } = options
  
  // 响应式状态
  const isDragging = ref(false)
  const position = reactive<Position>({ x: 0, y: 0 })
  const startPos = reactive<Position>({ x: 0, y: 0 })
  const dragStartPos = reactive<Position>({ x: 0, y: 0 })
  
  // 内部状态
  let originalTransition: string | null = null
  let rafId: number | null = null
  let hasMoved = false
  
  // 边界检测
  const getBounds = (): { minX: number; minY: number; maxX: number; maxY: number } => {
    if (!targetRef.value) {
      return { minX: 0, minY: 0, maxX: Infinity, maxY: Infinity }
    }
    
    const element = targetRef.value
    const rect = element.getBoundingClientRect()
    
    switch (bounds) {
      case 'viewport':
        return {
          minX: 0,
          minY: 0,
          maxX: window.innerWidth - rect.width,
          maxY: window.innerHeight - rect.height
        }
      
      case 'parent':
        const parent = element.parentElement
        if (!parent) {
          return { minX: 0, minY: 0, maxX: Infinity, maxY: Infinity }
        }
        const parentRect = parent.getBoundingClientRect()
        return {
          minX: 0,
          minY: 0,
          maxX: parentRect.width - rect.width,
          maxY: parentRect.height - rect.height
        }
      
      default:
        if (bounds instanceof HTMLElement) {
          const boundsRect = bounds.getBoundingClientRect()
          return {
            minX: boundsRect.left,
            minY: boundsRect.top,
            maxX: boundsRect.right - rect.width,
            maxY: boundsRect.bottom - rect.height
          }
        }
        return { minX: 0, minY: 0, maxX: Infinity, maxY: Infinity }
    }
  }
  
  // 约束位置在边界内
  const constrainPosition = (x: number, y: number): Position => {
    const bounds = getBounds()
    return {
      x: Math.max(bounds.minX, Math.min(x, bounds.maxX)),
      y: Math.max(bounds.minY, Math.min(y, bounds.maxY))
    }
  }
  
  // 更新位置（使用transform优化性能）
  const updatePosition = (x: number, y: number) => {
    if (!targetRef.value) return
    
    const constrained = constrainPosition(x, y)
    position.x = constrained.x
    position.y = constrained.y
    
    // 使用transform而不是top/left避免重排
    if (rafId) {
      cancelAnimationFrame(rafId)
    }
    
    rafId = requestAnimationFrame(() => {
      if (targetRef.value) {
        targetRef.value.style.transform = `translate(${constrained.x}px, ${constrained.y}px)`
      }
    })
  }
  
  // 鼠标按下事件
  const handleMouseDown = (e: MouseEvent) => {
    if (disabled || !(e.target as HTMLElement).closest('.window-header')) {
      return
    }
    
    e.preventDefault()
    e.stopPropagation()
    
    if (!targetRef.value) return
    
    // 保存原始过渡效果
    originalTransition = targetRef.value.style.transition
    targetRef.value.style.transition = 'none'
    
    // 记录起始位置
    dragStartPos.x = e.clientX
    dragStartPos.y = e.clientY
    
    const rect = targetRef.value.getBoundingClientRect()
    startPos.x = rect.left
    startPos.y = rect.top
    
    isDragging.value = true
    hasMoved = false
    
    // 添加拖拽样式
    if (draggingClass) {
      targetRef.value.classList.add(draggingClass)
    }
    
    // 添加全局事件监听
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    
    // 防止文本选择
    document.body.style.userSelect = 'none'
  }
  
  // 鼠标移动事件
  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging.value) return
    
    e.preventDefault()
    
    const deltaX = e.clientX - dragStartPos.x
    const deltaY = e.clientY - dragStartPos.y
    
    // 检查是否超过阈值
    if (!hasMoved && (Math.abs(deltaX) > threshold || Math.abs(deltaY) > threshold)) {
      hasMoved = true
    }
    
    if (hasMoved) {
      const newX = startPos.x + deltaX
      const newY = startPos.y + deltaY
      updatePosition(newX, newY)
    }
  }
  
  // 鼠标释放事件
  const handleMouseUp = (e: MouseEvent) => {
    if (!isDragging.value) return
    
    isDragging.value = false
    hasMoved = false
    
    if (targetRef.value) {
      // 恢复过渡效果
      if (originalTransition !== null) {
        targetRef.value.style.transition = originalTransition
      }
      
      // 移除拖拽样式
      if (draggingClass) {
        targetRef.value.classList.remove(draggingClass)
      }
      
      // 清理transform
      targetRef.value.style.transform = ''
    }
    
    // 移除全局事件监听
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    
    // 恢复文本选择
    document.body.style.userSelect = ''
    
    // 如果有实际移动，触发回调
    if (hasMoved && onDragEnd) {
      onDragEnd(position.x, position.y)
    }
  }
  
  // 外部回调函数
  let onDragEnd: ((x: number, y: number) => void) | null = null
  
  // 设置拖拽结束回调
  const setOnDragEnd = (callback: (x: number, y: number) => void) => {
    onDragEnd = callback
  }
  
  // 手动设置位置
  const setPosition = (x: number, y: number) => {
    const constrained = constrainPosition(x, y)
    position.x = constrained.x
    position.y = constrained.y
    
    if (targetRef.value) {
      targetRef.value.style.left = constrained.x + 'px'
      targetRef.value.style.top = constrained.y + 'px'
    }
  }
  
  // 重置位置
  const resetPosition = () => {
    setPosition(0, 0)
  }
  
  // 启用/禁用拖拽
  const enable = () => {
    if (targetRef.value) {
      targetRef.value.style.cursor = 'move'
    }
  }
  
  const disable = () => {
    if (targetRef.value) {
      targetRef.value.style.cursor = ''
    }
  }
  
  // 生命周期
  onMounted(() => {
    if (!disabled && targetRef.value) {
      targetRef.value.addEventListener('mousedown', handleMouseDown)
      enable()
    }
  })
  
  onUnmounted(() => {
    if (targetRef.value) {
      targetRef.value.removeEventListener('mousedown', handleMouseDown)
    }
    
    // 清理事件监听
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    
    // 清理动画帧
    if (rafId) {
      cancelAnimationFrame(rafId)
    }
    
    // 恢复样式
    if (targetRef.value) {
      targetRef.value.style.cursor = ''
      targetRef.value.style.transition = originalTransition || ''
      targetRef.value.style.transform = ''
      if (draggingClass) {
        targetRef.value.classList.remove(draggingClass)
      }
    }
    
    document.body.style.userSelect = ''
  })
  
  return {
    // 状态
    isDragging,
    position: readonly(position),
    
    // 方法
    setPosition,
    resetPosition,
    enable,
    disable,
    setOnDragEnd
  }
}

// 工具函数：创建只读引用
function readonly<T extends object>(obj: T): Readonly<T> {
  return obj as Readonly<T>
}