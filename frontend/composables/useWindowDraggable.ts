// composables/useWindowDraggable.ts
// 专为WindowContainer设计的简化拖拽Hook
import { ref, Ref } from 'vue';

interface Position {
  x: number;
  y: number;
}

export function useWindowDraggable(
  targetRef: Ref<HTMLElement | null>,
  options: {
    initialValue?: { x: number; y: number };
    handle?: Ref<HTMLElement | null>;
    disabled?: Ref<boolean> | { value: boolean };
  } = {}
) {
  const {
    initialValue = { x: 0, y: 0 },
    handle = null,
    disabled = { value: false }
  } = options;

  const position = ref({ ...initialValue });
  const isDragging = ref(false);
  
  const handleMouseDown = (e: MouseEvent) => {
    // 检查是否禁用
    if (disabled.value) return;
    
    // 检查是否点击在手柄上
    const target = handle?.value || targetRef.value;
    if (!target || !target.contains(e.target as Node)) return;
    
    e.preventDefault();
    e.stopPropagation();
    
    isDragging.value = true;
    
    const startX = e.clientX - position.value.x;
    const startY = e.clientY - position.value.y;
    
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.value) return;
      
      e.preventDefault();
      position.value.x = e.clientX - startX;
      position.value.y = e.clientY - startY;
    };
    
    const handleMouseUp = () => {
      isDragging.value = false;
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  // 暴露给模板使用
  return { 
    position, 
    isDragging, 
    handleMouseDown 
  };
}