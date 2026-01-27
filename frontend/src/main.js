// 前端配置 - 分离后的API路径配置
const API_BASE = process.env.NODE_ENV === 'production' 
    ? 'http://your-server-domain.com/api'  // 生产环境
    : 'http://localhost:8000/api';           // 开发环境

const App = {
    token: localStorage.getItem('token'),
    windows: [],
    zIndex: 1000,
    selectedIcon: null,

    // --- 通用请求函数 ---
    async req(url, method = 'GET', data = null, isFile = false) {
        const headers = { 'Authorization': `Bearer ${this.token}` };
        if (!isFile) headers['Content-Type'] = 'application/json';
        
        const opts = { method, headers };
        if (data) opts.body = isFile ? data : JSON.stringify(data);
        
        try {
            const res = await fetch(API_BASE + url, opts);
            if (res.status === 401) { 
                location.reload(); 
                throw new Error('Auth'); 
            }
            if (!res.ok) throw new Error(`Error ${res.status}`);
            return method === 'DELETE' ? null : res.json();
        } catch (error) {
            console.error('API请求失败:', error);
            this.showToast('请求失败，请检查网络连接');
            throw error;
        }
    },

    // --- 登录处理 ---
    async handleLogin() {
        const u = document.getElementById('uid').value;
        const p = document.getElementById('pwd').value;
        
        try {
            const res = await fetch(API_BASE + '/token/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: u, password: p })
            });
            
            if (!res.ok) throw new Error('登录失败');
            
            const data = await res.json();
            this.token = data.access;
            localStorage.setItem('token', this.token);
            
            document.getElementById('login-screen').style.display = 'none';
            this.refreshDesktop();
            this.showToast('登录成功');
            
        } catch (error) {
            this.showToast('登录失败，请检查用户名密码');
        }
    },

    // --- 获取图标 HTML ---
    getIconHtml(item) {
        if (item.type === 'category') {
            return `<i class="fa-solid fa-folder fa-icon-lg" style="color:#f1c40f;"></i>`;
        }
        // 优先使用后端传来的 icon_class
        if (item.data.icon_class) {
            return `<i class="${item.data.icon_class} fa-icon-lg"></i>`;
        }
        // 根据类型提供默认图标
        const typeIcons = {
            'doc': 'fa-file',
            'image': 'fa-file-image',
            'video': 'fa-file-video',
            'audio': 'fa-file-audio',
            'archive': 'fa-file-zipper',
            'link': 'fa-link'
        };
        const icon = typeIcons[item.data.kind] || 'fa-file';
        return `<i class="fa-solid ${icon} fa-icon-lg"></i>`;
    },

    // --- 渲染桌面 ---
    async refreshDesktop() {
        const grid = document.getElementById('desktop-grid');
        grid.innerHTML = '';
        
        try {
            const data = await this.req('/desktop/?parent_id=root');
            (data.results || data || []).forEach(item => {
                const el = document.createElement('div');
                el.className = 'icon';
                el.ondblclick = () => this.openItem(item);
                el.oncontextmenu = (e) => {
                    e.preventDefault();
                    this.selectedIcon = item;
                    this.showContextMenu(e.pageX, e.pageY);
                };
                
                el.innerHTML = `
                    <div class="icon-body">
                        ${this.getIconHtml(item)}
                        ${item.preview && item.preview.length > 0 ? 
                            item.preview.map(p => p.cover ? `<img src="${p.cover}" class="icon-thumb">` : '').join('') : ''}
                    </div>
                    <div class="icon-text">${item.title}</div>
                `;
                
                grid.appendChild(el);
            });
        } catch (error) {
            console.error('加载桌面失败:', error);
        }
    },

    // --- 创建窗口 ---
    async createWindow(id, title, type = 'folder', contentData = null) {
        // 防止重复打开相同窗口
        if (this.windows.find(w => w.id === id)) {
            this.focusWin(id);
            return;
        }

        const win = document.createElement('div');
        win.className = 'window';
        win.id = 'win-' + id;
        win.style.zIndex = ++this.zIndex;
        win.style.left = '100px';
        win.style.top = '50px';

        // 侧边栏 HTML (如果是文件夹类型)
        let bodyHtml = '';
        if (type === 'folder') {
            // 获取侧边栏分类列表
            const categories = await this.req('/categories/');
            let sidebarItems = categories.results.map(c => 
                `<div class="sidebar-item" onclick="App.loadFolderContent('${c.id}', document.getElementById('win-${id}'), this)">
                    <i class="fa-solid fa-${c.icon || 'folder'}"></i> ${c.name}
                </div>`
            ).join('');
            
            // 添加 "桌面" 和 "根目录"
            sidebarItems = `
                <div class="sidebar-item" onclick="App.loadFolderContent('root', document.getElementById('win-${id}'), this)">
                    <i class="fa-solid fa-desktop"></i> 桌面
                </div>
                ${sidebarItems}
            `;

            bodyHtml = `
                <div class="win-sidebar">${sidebarItems}</div>
                <div class="win-content"></div>
            `;
        }

        win.innerHTML = `
            <div class="win-header">
                <div class="win-controls">
                    <button class="win-btn btn-close" onclick="App.closeWin('${id}')">×</button>
                    <button class="win-btn btn-min" onclick="App.minWin('${id}')">-</button>
                    <button class="win-btn btn-max" onclick="App.maxWin('${id}')"></button>
                </div>
                <div class="win-title">${title}</div>
                <div style="width:40px"></div>
            </div>
            <div class="win-body" style="${type!=='folder'?'display:block':''}">${bodyHtml}</div>
        `;
        
        // 拖拽绑定
        const header = win.querySelector('.win-header');
        header.onmousedown = (e) => {
            this.dragWin(win, e);
        };

        document.body.appendChild(win);
        this.windows.push({id, el: win});
        this.addToDock(id, title);

        setTimeout(() => win.classList.add('open'), 10);

        if (type === 'folder') {
            // 默认加载指定文件夹
            this.loadFolderContent(contentData, win);
        }
    },

    // --- 窗口管理函数 ---
    focusWin(id) {
        const win = this.windows.find(w => w.id === id);
        if (win) {
            win.el.style.zIndex = ++this.zIndex;
            // 高亮Dock栏
            document.querySelectorAll('.dock-item').forEach(el => el.classList.remove('active'));
            const dockItem = document.querySelector(`[onclick*="'${id}'"]`);
            if (dockItem) dockItem.classList.add('active');
        }
    },

    closeWin(id) {
        const win = this.windows.find(w => w.id === id);
        if (win) {
            win.el.remove();
            this.windows = this.windows.filter(w => w.id !== id);
            this.removeFromDock(id);
        }
    },

    minWin(id) {
        const win = this.windows.find(w => w.id === id);
        if (win) {
            win.el.classList.toggle('minimized');
        }
    },

    maxWin(id) {
        const win = this.windows.find(w => w.id === id);
        if (win) {
            const isMax = win.el.style.width === 'calc(100% - 20px)';
            win.el.style.width = isMax ? '600px' : 'calc(100% - 20px)';
            win.el.style.height = isMax ? '400px' : 'calc(100% - 100px)';
            win.el.style.left = isMax ? '10px' : '100px';
            win.el.style.top = isMax ? '10px' : '50px';
        }
    },

    dragWin(win, e) {
        e.preventDefault();
        const startX = e.clientX;
        const startY = e.clientY;
        const startLeft = parseInt(win.style.left) || 0;
        const startTop = parseInt(win.style.top) || 0;

        const onMouseMove = (e) => {
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            win.style.left = (startLeft + dx) + 'px';
            win.style.top = (startTop + dy) + 'px';
        };

        const onMouseUp = () => {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
        };

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
    },

    // --- Dock栏管理 ---
    addToDock(id, title) {
        const dockApps = document.getElementById('dock-apps');
        if (!dockApps.querySelector(`[onclick*="'${id}'"]`)) {
            const div = document.createElement('div');
            div.className = 'dock-item';
            div.innerHTML = `<i class="fa-solid fa-window-maximize"></i>`;
            div.onclick = () => this.focusWin(id);
            dockApps.appendChild(div);
        }
    },

    removeFromDock(id) {
        const dockApps = document.getElementById('dock-apps');
        const item = dockApps.querySelector(`[onclick*="'${id}'"]`);
        if (item) item.remove();
    },

    // --- 加载文件夹内容到右侧区域 ---
    async loadFolderContent(parentId, winEl, sidebarItemEl) {
        const contentDiv = winEl.querySelector('.win-content');
        if (!contentDiv) return;

        // 侧边栏高亮处理
        if (sidebarItemEl) {
            winEl.querySelectorAll('.sidebar-item').forEach(el => el.classList.remove('active'));
            sidebarItemEl.classList.add('active');
        }

        contentDiv.innerHTML = '<div style="color:#888; width:100%; text-align:center; padding-top:20px;">加载中...</div>';
        
        try {
            const data = await this.req(`/desktop/?parent_id=${parentId}`);
            const list = data.results || data || [];
            
            contentDiv.innerHTML = '';
            if (list.length === 0) {
                contentDiv.innerHTML = '<div style="color:#ccc; width:100%; text-align:center; margin-top:50px;">此文件夹为空</div>';
                return;
            }

            list.forEach(item => {
                const el = document.createElement('div');
                el.className = 'icon';
                el.style.height = '90px';
                el.style.width = '90px';
                el.ondblclick = () => this.openItem(item);
                
                el.innerHTML = `
                    <div class="icon-body">
                        ${this.getIconHtml(item)}
                    </div>
                    <div class="icon-text">${item.title}</div>
                `;
                
                contentDiv.appendChild(el);
            });
        } catch (error) {
            contentDiv.innerHTML = '<div style="color:red; width:100%; text-align:center; padding-top:20px;">加载失败</div>';
        }
    },

    // --- 打开项目 (支持 PDF 预览) ---
    openItem(item) {
        if (item.type === 'category') {
            this.createWindow(item.id, item.title, 'folder', item.id);
        } else if (item.type === 'resource') {
            const url = item.data.file || item.data.link;
            if (!url) return;

            // 增强预览逻辑
            if (url.endsWith('.pdf')) {
                this.createWindow('pdf-' + item.id, item.title, 'pdf', url);
            } else if (url.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
                this.createWindow('img-' + item.id, item.title, 'image', url);
            } else if (url.match(/^https?:\/\//)) {
                window.open(url, '_blank');
            } else {
                // 其他文件类型，尝试在新窗口打开
                window.open(url, '_blank');
            }
        }
    },

    // --- 右键菜单 ---
    showContextMenu(x, y) {
        const menu = document.getElementById('context-menu');
        menu.style.left = x + 'px';
        menu.style.top = y + 'px';
        menu.style.display = 'block';
        
        // 点击其他地方关闭菜单
        const closeMenu = () => {
            menu.style.display = 'none';
            document.removeEventListener('click', closeMenu);
        };
        setTimeout(() => document.addEventListener('click', closeMenu), 100);
    },

    // --- 右键菜单操作 ---
    openSelected() {
        if (this.selectedIcon) {
            this.openItem(this.selectedIcon);
        }
    },

    async renameSelected() {
        if (!this.selectedIcon) return;
        
        const newName = prompt('请输入新名称:', this.selectedIcon.title);
        if (newName && newName !== this.selectedIcon.title) {
            try {
                await this.req(`/desktop/${this.selectedIcon.id}/rename/`, 'POST', { name: newName });
                this.refreshDesktop();
                this.showToast('重命名成功');
            } catch (error) {
                this.showToast('重命名失败');
            }
        }
    },

    async deleteSelected() {
        if (!this.selectedIcon || !confirm(`确定要删除 "${this.selectedIcon.title}" 吗？`)) return;
        
        try {
            await this.req(`/desktop/${this.selectedIcon.id}/uninstall/`, 'DELETE');
            this.refreshDesktop();
            this.showToast('删除成功');
        } catch (error) {
            this.showToast('删除失败');
        }
    },

    // --- 创建文件夹 ---
    async createFolder() {
        const name = prompt('请输入文件夹名称:', '新建文件夹');
        if (!name) return;
        
        try {
            await this.req('/desktop/create_folder/', 'POST', {
                name: name,
                x: Math.random() * 400 + 50,
                y: Math.random() * 300 + 50
            });
            this.refreshDesktop();
            this.showToast('文件夹创建成功');
        } catch (error) {
            this.showToast('创建失败');
        }
    },

    // --- 工具函数 ---
    showToast(msg) {
        const t = document.getElementById('toast');
        t.innerText = msg;
        t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), 2000);
    },

    openPC() { this.createWindow('pc', '我的电脑', 'folder', 'root'); },
    uploadTrigger() { document.getElementById('file-input').click(); },
    uploadFolderTrigger() { document.getElementById('folder-input').click(); },

    // --- 文件上传处理 (简化版) ---
    async handleUpload(input, isFolder = false) {
        const files = input.files;
        if (!files.length) return;
        
        try {
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('file', files[i]);
            }
            
            await this.req('/desktop/upload_file/', 'POST', formData, true);
            this.refreshDesktop();
            this.showToast('上传成功');
        } catch (error) {
            this.showToast('上传失败');
        }
        
        input.value = '';
    },

    // --- H5应用安装 ---
    async installH5App() {
        const nameInput = document.getElementById('h5-name');
        const fileInput = document.getElementById('h5-file');
        
        if (!nameInput.value || !fileInput.files[0]) {
            this.showToast('请填写应用名称并选择文件');
            return;
        }

        try {
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            formData.append('title', nameInput.value);
            formData.append('icon_class', 'fa-solid fa-gamepad');

            await this.req('/desktop/install_h5_app/', 'POST', formData, true);
            this.refreshDesktop();
            document.getElementById('install-modal').style.display = 'none';
            this.showToast('应用安装成功');
        } catch (error) {
            this.showToast('安装失败');
        }
    },

    showInstallModal() {
        document.getElementById('install-modal').style.display = 'flex';
    }
};

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', () => {
    // 检查是否已登录
    if (App.token) {
        document.getElementById('login-screen').style.display = 'none';
        App.refreshDesktop();
    }
    
    // 阻止默认右键菜单
    document.addEventListener('contextmenu', (e) => {
        if (e.target.closest('.icon') || e.target.closest('#desktop')) {
            e.preventDefault();
        }
    });
});