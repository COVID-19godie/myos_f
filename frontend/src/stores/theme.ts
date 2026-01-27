import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useThemeStore = defineStore('theme', () => {
  // 状态
  const isDark = ref(localStorage.getItem('theme-dark') === 'true');
  const wallpaper = ref(localStorage.getItem('theme-wallpaper') || 'https://images.unsplash.com/photo-1477346611705-65d1883cee1e?q=80&w=2070&auto=format&fit=crop');

  // 动作：应用主题到 DOM
  const applyTheme = () => {
    const html = document.documentElement;
    if (isDark.value) {
      html.classList.add('dark');
      // 这里的 color-scheme 是为了让浏览器原生控件(滚动条等)也变黑
      html.style.colorScheme = 'dark'; 
    } else {
      html.classList.remove('dark');
      html.style.colorScheme = 'light';
    }
  };

  // 动作：切换模式
  const toggleDark = () => {
    isDark.value = !isDark.value;
    localStorage.setItem('theme-dark', isDark.value.toString());
    applyTheme();
  };

  // 动作：设置壁纸
  const setWallpaper = (url: string) => {
    wallpaper.value = url;
    localStorage.setItem('theme-wallpaper', url);
  };

  // 初始化执行
  applyTheme();

  return { isDark, wallpaper, toggleDark, setWallpaper, applyTheme };
});