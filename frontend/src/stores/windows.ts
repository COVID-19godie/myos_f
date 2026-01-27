import { defineStore } from 'pinia'

interface WindowInstance {
  id: string;
  title: string;
  type: 'folder' | 'iframe' | 'app' | 'pdf' | 'image';
  content?: any;
  zIndex: number;
  isMinimized: boolean;
  isMaximized: boolean;
  x: number;
  y: number;
  width?: number;
  height?: number;
}

export const useWindowStore = defineStore('windows', {
  state: () => ({
    instances: [] as WindowInstance[],
    activeId: '',
    topZIndex: 1000
  }),
  actions: {
    createWindow(title: string, type: WindowInstance['type'], content: any, width = 600, height = 400) {
      const id = Date.now().toString();
      this.topZIndex++;
      this.instances.push({
        id, 
        title, 
        type, 
        content,
        zIndex: this.topZIndex,
        isMinimized: false,
        isMaximized: false,
        x: 100 + (this.instances.length * 20),
        y: 50 + (this.instances.length * 20),
        width,
        height
      });
      this.activeId = id;
      return id;
    },
    focusWindow(id: string) {
      this.activeId = id;
      const win = this.instances.find(w => w.id === id);
      if (win) {
        this.topZIndex++;
        win.zIndex = this.topZIndex;
        win.isMinimized = false;
      }
    },
    closeWindow(id: string) {
      this.instances = this.instances.filter(w => w.id !== id);
      if (this.activeId === id) {
        this.activeId = '';
      }
    },
    minimizeWindow(id: string) {
      const win = this.instances.find(w => w.id === id);
      if (win) {
        win.isMinimized = !win.isMinimized;
      }
    },
    maximizeWindow(id: string) {
      const win = this.instances.find(w => w.id === id);
      if (win) {
        win.isMaximized = !win.isMaximized;
      }
    },
    updateWindowPosition(id: string, x: number, y: number) {
      const win = this.instances.find(w => w.id === id);
      if (win) {
        win.x = x;
        win.y = y;
      }
    }
  }
})