// 全局变量 - 自动检测后端地址
const getApiBase = () => {
    // 优先使用相对路径，便于部署
    if (window.location.port === '3000') {
        // 前端开发服务器，连接到后端
        return 'http://localhost:8001/api';
    } else if (window.location.port === '8001') {
        // 直接访问后端，使用相对路径
        return '/api';
    } else {
        // 默认情况
        return 'http://localhost:8001/api';
    }
};

const API_BASE = getApiBase();
console.log('API Base URL:', API_BASE);

let currentUser = null;
let authMode = 'login'; // login or register

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    checkAuthStatus();
    loadFileCategories();
    loadRecentFiles();
    setupEventListeners();
});

// 应用初始化
function initializeApp() {
    console.log('ZMG Cloud OS 初始化...');
    
    // 设置用户名显示
    const username = localStorage.getItem('username');
    if (username) {
        document.getElementById('usernameDisplay').textContent = username;
        
        // 设置用户头像
        const avatar = document.getElementById('userAvatar');
        avatar.innerHTML = username.charAt(0).toUpperCase();
        avatar.onclick = () => openModal('authModal');
    }
}

// 检查认证状态
function checkAuthStatus() {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!token || !refreshToken) {
        // 未登录，显示登录弹窗
        setTimeout(() => {
            openModal('authModal');
        }, 1000);
        return;
    }
    
    // 验证token有效性
    verifyToken(token).then(isValid => {
        if (!isValid) {
            // token无效，尝试刷新
            refreshAccessToken(refreshToken).then(success => {
                if (!success) {
                    // 刷新失败，清除token并显示登录
                    clearAuthData();
                    setTimeout(() => {
                        openModal('authModal');
                    }, 1000);
                }
            });
        }
    });
}

// 验证token
async function verifyToken(token) {
    try {
        const response = await fetch(`${API_BASE}/verify/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        return response.ok;
    } catch (error) {
        console.error('Token verification failed:', error);
        return false;
    }
}

// 刷新token
async function refreshAccessToken(refreshToken) {
    try {
        const response = await fetch(`${API_BASE}/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return true;
        }
    } catch (error) {
        console.error('Token refresh failed:', error);
    }
    return false;
}

// 设置事件监听器
function setupEventListeners() {
    // 搜索功能
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    
    // 认证表单
    const authForm = document.getElementById('authForm');
    authForm.addEventListener('submit', handleAuthSubmit);
    
    // 点击遮罩关闭弹窗
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });
    
    // ESC键关闭弹窗
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                closeModal(modal.id);
            });
        }
    });
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 搜索处理
function handleSearch(event) {
    const query = event.target.value.trim();
    if (query.length > 0) {
        console.log('搜索:', query);
        // 实现搜索逻辑
        performSearch(query);
    }
}

// 执行搜索
async function performSearch(query) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE}/search/?q=${encodeURIComponent(query)}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const files = await response.json();
            displaySearchResults(files);
        }
    } catch (error) {
        console.error('搜索失败:', error);
    }
}

// 显示搜索结果
function displaySearchResults(files) {
    // 实现搜索结果展示
    console.log('搜索结果:', files);
}

// 加载文件分类
async function loadFileCategories() {
    const categories = ['documents', 'images', 'videos', 'music', 'downloads', 'recent'];
    
    for (const category of categories) {
        try {
            const count = await getFileCountByCategory(category);
            updateCategoryCount(category, count);
        } catch (error) {
            console.error(`加载${category}分类失败:`, error);
        }
    }
}

// 获取分类文件数量
async function getFileCountByCategory(category) {
    // 模拟数据，实际应从API获取
    const mockCounts = {
        documents: 15,
        images: 42,
        videos: 8,
        music: 23,
        downloads: 12,
        recent: 10
    };
    
    return new Promise(resolve => {
        setTimeout(() => resolve(mockCounts[category] || 0), 200);
    });
}

// 更新分类数量显示
function updateCategoryCount(category, count) {
    const element = document.getElementById(`${category}-count`);
    if (element) {
        element.textContent = `${count} 个项目`;
    }
}

// 打开分类
function openCategory(category) {
    console.log(`打开分类: ${category}`);
    // 实现打开分类逻辑
    loadFilesByCategory(category);
}

// 加载分类文件
async function loadFilesByCategory(category) {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE}/files/category/${category}/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const files = await response.json();
            displayFiles(files);
        }
    } catch (error) {
        console.error('加载分类文件失败:', error);
    }
}

// 加载最近文件
async function loadRecentFiles() {
    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE}/files/`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const files = await response.json();
            displayFiles(files);
        } else {
            // API不可用，显示模拟数据
            displayMockFiles();
        }
    } catch (error) {
        console.error('加载最近文件失败:', error);
        // 显示模拟数据
        displayMockFiles();
    }
}

// 显示模拟文件数据
function displayMockFiles() {
    const mockFiles = [
        { name: '工作报告.docx', type: 'document', icon: 'fa-file-word' },
        { name: '项目截图.png', type: 'image', icon: 'fa-file-image' },
        { name: '演示视频.mp4', type: 'video', icon: 'fa-file-video' },
        { name: '音乐文件.mp3', type: 'music', icon: 'fa-file-audio' },
        { name: '代码文件.js', type: 'code', icon: 'fa-file-code' },
        { name: '压缩包.zip', type: 'archive', icon: 'fa-file-archive' },
        { name: '表格数据.xlsx', type: 'document', icon: 'fa-file-excel' },
        { name: 'PDF文档.pdf', type: 'document', icon: 'fa-file-pdf' }
    ];
    
    displayFiles(mockFiles);
}

// 显示文件
function displayFiles(files) {
    const fileGrid = document.getElementById('fileGrid');
    fileGrid.innerHTML = '';
    
    files.forEach(file => {
        const fileItem = createFileItem(file);
        fileGrid.appendChild(fileItem);
    });
}

// 创建文件项
function createFileItem(file) {
    const item = document.createElement('div');
    item.className = 'file-item';
    item.onclick = () => openFile(file);
    
    const iconClass = getFileIcon(file.type, file.name);
    
    item.innerHTML = `
        <i class="fas ${iconClass} file-icon icon-${file.type}"></i>
        <div class="file-name">${file.name}</div>
    `;
    
    return item;
}

// 获取文件图标
function getFileIcon(type, filename) {
    const extension = filename.split('.').pop().toLowerCase();
    
    const iconMap = {
        'document': {
            'doc': 'fa-file-word',
            'docx': 'fa-file-word',
            'pdf': 'fa-file-pdf',
            'xls': 'fa-file-excel',
            'xlsx': 'fa-file-excel',
            'ppt': 'fa-file-powerpoint',
            'pptx': 'fa-file-powerpoint',
            'txt': 'fa-file-alt',
            'default': 'fa-file-alt'
        },
        'image': 'fa-file-image',
        'video': 'fa-file-video',
        'music': 'fa-file-audio',
        'code': 'fa-file-code',
        'archive': 'fa-file-archive',
        'app': 'fa-file-code'
    };
    
    if (type === 'document' && iconMap.document[extension]) {
        return iconMap.document[extension];
    }
    
    return iconMap[type] || 'fa-file';
}

// 打开文件
function openFile(file) {
    console.log('打开文件:', file);
    // 实现打开文件逻辑
    alert(`正在打开: ${file.name}`);
}

// 弹窗管理
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // 根据弹窗类型执行特定逻辑
        if (modalId === 'authModal') {
            updateAuthModal();
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // 清空表单
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
            clearFormErrors();
        }
    }
}

// 更新认证弹窗
function updateAuthModal() {
    const token = localStorage.getItem('access_token');
    
    if (token) {
        // 已登录，显示用户信息
        document.getElementById('authModalTitle').textContent = '账户信息';
        document.getElementById('authModalSubtitle').textContent = '管理您的账户';
        document.getElementById('authSubmitText').textContent = '退出登录';
        document.getElementById('authSwitchBtn').textContent = '返回主页';
        document.getElementById('authSwitchBtn').onclick = () => closeModal('authModal');
        
        // 隐藏表单，显示用户信息
        const usernameGroup = document.getElementById('usernameGroup');
        const passwordGroup = document.getElementById('passwordGroup');
        usernameGroup.style.display = 'none';
        passwordGroup.style.display = 'none';
        
        // 显示用户信息
        if (!document.getElementById('userInfoDisplay')) {
            const userInfo = document.createElement('div');
            userInfo.id = 'userInfoDisplay';
            userInfo.innerHTML = `
                <div style="text-align: center; margin-bottom: 20px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                    <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #007aff, #0056d6); border-radius: 50%; margin: 0 auto 15px; display: flex; align-items: center; justify-content: center; color: white; font-size: 24px; font-weight: 600;">
                        ${localStorage.getItem('username')?.charAt(0).toUpperCase() || 'U'}
                    </div>
                    <h4 style="margin-bottom: 5px;">${localStorage.getItem('username') || '用户'}</h4>
                    <p style="color: #666; font-size: 14px;">已登录</p>
                </div>
            `;
            document.getElementById('authForm').insertBefore(userInfo, document.getElementById('authSubmitBtn'));
        }
    } else {
        // 未登录，显示登录表单
        document.getElementById('authModalTitle').textContent = authMode === 'login' ? '用户登录' : '用户注册';
        document.getElementById('authModalSubtitle').textContent = authMode === 'login' ? '请输入您的账号信息' : '创建新账户';
        document.getElementById('authSubmitText').textContent = authMode === 'login' ? '登录' : '注册';
        document.getElementById('authSwitchBtn').textContent = authMode === 'login' ? '没有账号？立即注册' : '已有账号？立即登录';
        
        // 显示表单
        const usernameGroup = document.getElementById('usernameGroup');
        const passwordGroup = document.getElementById('passwordGroup');
        usernameGroup.style.display = 'block';
        passwordGroup.style.display = 'block';
        
        // 移除用户信息
        const userInfo = document.getElementById('userInfoDisplay');
        if (userInfo) {
            userInfo.remove();
        }
    }
}

// 切换认证模式
function switchAuthMode() {
    const token = localStorage.getItem('access_token');
    
    if (token) {
        // 已登录，点击返回主页
        closeModal('authModal');
        return;
    }
    
    // 切换登录/注册模式
    authMode = authMode === 'login' ? 'register' : 'login';
    updateAuthModal();
    clearFormErrors();
}

// 处理认证提交
async function handleAuthSubmit(event) {
    event.preventDefault();
    
    const token = localStorage.getItem('access_token');
    
    if (token) {
        // 已登录，执行退出
        handleLogout();
        return;
    }
    
    // 执行登录/注册
    const username = document.getElementById('authUsername').value.trim();
    const password = document.getElementById('authPassword').value;
    
    if (!validateAuthForm(username, password)) {
        return;
    }
    
    showAuthLoading(true);
    
    try {
        if (authMode === 'login') {
            await handleLogin(username, password);
        } else {
            await handleRegister(username, password);
        }
    } catch (error) {
        showFormError('authSubmitBtn', error.message);
    } finally {
        showAuthLoading(false);
    }
}

// 处理登录
async function handleLogin(username, password) {
    try {
        const response = await fetch(`${API_BASE}/token/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            
            // 保存认证数据
            localStorage.setItem('access_token', data.access);
            localStorage.setItem('refresh_token', data.refresh);
            localStorage.setItem('username', username);
            
            // 更新UI
            document.getElementById('usernameDisplay').textContent = username;
            const avatar = document.getElementById('userAvatar');
            avatar.innerHTML = username.charAt(0).toUpperCase();
            
            closeModal('authModal');
            
            // 显示成功消息
            showNotification('登录成功！', 'success');
        } else {
            const errorData = await response.json();
            throw new Error(errorData.detail || '登录失败，请检查用户名和密码');
        }
    } catch (error) {
        throw new Error(error.message || '网络错误，请检查后端服务');
    }
}

// 处理注册
async function handleRegister(username, password) {
    try {
        // 这里需要实现注册API
        // 临时模拟注册成功
        showNotification('注册功能开发中，请联系管理员创建账号', 'info');
        
        // 切换回登录模式
        authMode = 'login';
        updateAuthModal();
    } catch (error) {
        throw new Error(error.message || '注册失败');
    }
}

// 处理退出登录
function handleLogout() {
    if (confirm('确定要退出登录吗？')) {
        clearAuthData();
        closeModal('authModal');
        showNotification('已退出登录', 'info');
        
        // 刷新页面
        setTimeout(() => {
            location.reload();
        }, 1000);
    }
}

// 清除认证数据
function clearAuthData() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
}

// 验证表单
function validateAuthForm(username, password) {
    clearFormErrors();
    
    let isValid = true;
    
    if (!username || username.length < 3) {
        showFieldError('usernameGroup', 'usernameError', '用户名至少需要3个字符');
        isValid = false;
    }
    
    if (!password || password.length < 6) {
        showFieldError('passwordGroup', 'passwordError', '密码至少需要6个字符');
        isValid = false;
    }
    
    return isValid;
}

// 显示字段错误
function showFieldError(groupId, errorId, message) {
    const group = document.getElementById(groupId);
    const error = document.getElementById(errorId);
    const input = group.querySelector('input');
    
    input.classList.add('error');
    error.textContent = message;
    error.style.display = 'block';
}

// 显示表单错误
function showFormError(buttonId, message) {
    const button = document.getElementById(buttonId);
    const originalText = button.innerHTML;
    
    button.innerHTML = `<span style="color: #ff3b30;">${message}</span>`;
    button.disabled = true;
    
    setTimeout(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    }, 3000);
}

// 清除表单错误
function clearFormErrors() {
    document.querySelectorAll('.error-text').forEach(error => {
        error.textContent = '';
        error.style.display = 'none';
    });
    
    document.querySelectorAll('input.error').forEach(input => {
        input.classList.remove('error');
    });
}

// 显示/隐藏加载状态
function showAuthLoading(show) {
    const submitBtn = document.getElementById('authSubmitBtn');
    const loading = document.getElementById('authLoading');
    const switchBtn = document.getElementById('authSwitchBtn');
    
    if (show) {
        submitBtn.style.display = 'none';
        switchBtn.style.display = 'none';
        loading.style.display = 'block';
    } else {
        submitBtn.style.display = 'block';
        switchBtn.style.display = 'block';
        loading.style.display = 'none';
    }
}

// 测试Alist连接
function testAlistConnection() {
    showNotification('Alist连接测试功能开发中...', 'info');
}

// 处理文件上传
function handleFileUpload(event) {
    const files = event.target.files;
    if (files.length > 0) {
        console.log('选择文件:', files);
        showNotification(`已选择 ${files.length} 个文件`, 'info');
        // 实现文件上传逻辑
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    // 创建通知元素
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#34c759' : type === 'error' ? '#ff3b30' : '#007aff'};
        color: white;
        border-radius: 10px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
        z-index: 3000;
        font-size: 14px;
        max-width: 300px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // 显示动画
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // 自动隐藏
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// 导出全局函数供HTML调用
window.openModal = openModal;
window.closeModal = closeModal;
window.switchAuthMode = switchAuthMode;
window.openCategory = openCategory;
window.testAlistConnection = testAlistConnection;
window.handleFileUpload = handleFileUpload;