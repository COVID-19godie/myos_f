/**
 * 智能API管理器 - 自动发现和连接后端API
 * 支持多种连接方式：代理、直连、环境变量
 */

class SmartApiManager {
    constructor() {
        this.baseURL = null;
        this.apiVersion = 'v1';
        this.discoveryAttempts = 0;
        this.maxDiscoveryAttempts = 3;
        this.fallbackPorts = [8001, 8000, 8080, 9000];
        this.init();
    }

    async init() {
        console.log('🔍 开始智能API发现...');
        await this.discoverApi();
    }

    /**
     * 智能发现API端点
     */
    async discoverApi() {
        try {
            // 1. 首先检查环境变量
            const envApi = this.checkEnvironmentVariables();
            if (envApi) {
                console.log('✅ 使用环境变量API:', envApi);
                this.baseURL = envApi;
                return;
            }

            // 2. 检查Vite代理（开发环境）
            if (this.isDevelopment()) {
                const proxyApi = this.checkViteProxy();
                if (proxyApi) {
                    console.log('✅ 使用Vite代理API');
                    this.baseURL = proxyApi;
                    return;
                }
            }

            // 3. 尝试连接常见端口
            const discovered = await this.tryCommonPorts();
            if (discovered) {
                console.log('✅ 发现可用API:', this.baseURL);
                return;
            }

            // 4. 使用相对路径作为最后备选
            console.log('⚠️ 使用相对路径API');
            this.baseURL = '/api';

        } catch (error) {
            console.error('❌ API发现失败:', error);
            this.useFallback();
        }
    }

    /**
     * 检查环境变量
     */
    checkEnvironmentVariables() {
        // 浏览器环境
        if (typeof process !== 'undefined' && process.env) {
            return process.env.VITE_API_BASE_URL || 
                   process.env.REACT_APP_API_BASE_URL;
        }

        // 前端环境
        return (
            import.meta.env?.VITE_API_BASE_URL ||
            import.meta.env?.REACT_APP_API_BASE_URL ||
            null
        );
    }

    /**
     * 检查Vite代理配置
     */
    checkViteProxy() {
        // 如果是通过Vite开发服务器访问，使用相对路径
        if (window.location.port === '3000') {
            return '/api'; // Vite会代理到配置的target
        }
        return null;
    }

    /**
     * 尝试连接常见端口
     */
    async tryCommonPorts() {
        for (let port of this.fallbackPorts) {
            try {
                const url = `http://localhost:${port}/api/health/`;
                console.log(`🔍 尝试连接: ${url}`);
                
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    // 设置较短超时
                    signal: AbortSignal.timeout(2000)
                });

                if (response.ok) {
                    this.baseURL = `http://localhost:${port}/api`;
                    this.saveWorkingConfig(port);
                    return true;
                }
            } catch (error) {
                console.log(`❌ 端口 ${port} 连接失败:`, error.message);
                continue;
            }
        }
        return false;
    }

    /**
     * 保存工作配置到localStorage
     */
    saveWorkingConfig(port) {
        const config = {
            baseURL: `http://localhost:${port}/api`,
            port: port,
            timestamp: Date.now()
        };
        localStorage.setItem('zmg_api_config', JSON.stringify(config));
        console.log('💾 保存API配置:', config);
    }

    /**
     * 加载保存的配置
     */
    loadSavedConfig() {
        try {
            const saved = localStorage.getItem('zmg_api_config');
            if (saved) {
                const config = JSON.parse(saved);
                const now = Date.now();
                const dayInMs = 24 * 60 * 60 * 1000;
                
                // 配置不超过1天就使用
                if (now - config.timestamp < dayInMs) {
                    console.log('📋 加载保存的API配置:', config);
                    this.baseURL = config.baseURL;
                    return true;
                }
            }
        } catch (error) {
            console.warn('⚠️ 加载保存配置失败:', error);
        }
        return false;
    }

    /**
     * 使用备选方案
     */
    useFallback() {
        // 尝试加载之前成功的配置
        if (this.loadSavedConfig()) {
            return;
        }

        // 根据当前环境决定
        if (this.isDevelopment()) {
            this.baseURL = '/api'; // 依赖Vite代理
        } else {
            this.baseURL = window.location.origin + '/api'; // 同源部署
        }
        
        console.log('🔄 使用备选API配置:', this.baseURL);
    }

    /**
     * 检查是否为开发环境
     */
    isDevelopment() {
        return (
            window.location.hostname === 'localhost' ||
            window.location.hostname === '127.0.0.1' ||
            window.location.port === '3000'
        );
    }

    /**
     * 获取基础URL
     */
    getBaseURL() {
        if (!this.baseURL) {
            console.warn('⚠️ API基础URL未初始化，使用默认值');
            return '/api';
        }
        return this.baseURL;
    }

    /**
     * 构建完整URL
     */
    buildUrl(endpoint) {
        const base = this.getBaseURL();
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
        return `${base}/${cleanEndpoint}`;
    }

    /**
     * 通用请求方法
     */
    async request(endpoint, options = {}) {
        const url = this.buildUrl(endpoint);
        
        // 默认配置
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // 添加认证token
        const token = this.getAuthToken();
        if (token && !endpoint.includes('login')) {
            config.headers.Authorization = `Bearer ${token}`;
        }

        try {
            console.log(`🌐 API请求: ${config.method || 'GET'} ${url}`);
            const response = await fetch(url, config);
            
            // 处理认证失败
            if (response.status === 401) {
                this.handleAuthFailure();
                throw new Error('认证失败，请重新登录');
            }

            // 处理服务器错误
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`API错误 ${response.status}: ${errorText}`);
            }

            // 处理空响应
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else {
                return await response.text();
            }

        } catch (error) {
            console.error(`❌ API请求失败 ${url}:`, error);
            
            // 如果是网络错误，尝试重新发现API
            if (error.name === 'TypeError' || error.name === 'AbortError') {
                console.log('🔄 网络错误，尝试重新发现API...');
                await this.rediscover();
                // 重试一次
                return this.request(endpoint, options);
            }
            
            throw error;
        }
    }

    /**
     * 重新发现API
     */
    async rediscover() {
        if (this.discoveryAttempts >= this.maxDiscoveryAttempts) {
            console.error('❌ API重新发现次数超限');
            return;
        }
        
        this.discoveryAttempts++;
        this.baseURL = null;
        await this.discoverApi();
    }

    /**
     * 获取认证token
     */
    getAuthToken() {
        return (
            localStorage.getItem('access_token') ||
            localStorage.getItem('token') ||
            null
        );
    }

    /**
     * 处理认证失败
     */
    handleAuthFailure() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        
        // 如果不是登录页面，重定向到登录
        if (!window.location.pathname.includes('login')) {
            setTimeout(() => {
                window.location.href = '/login.html';
            }, 1000);
        }
    }

    /**
     * 便捷方法
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    /**
     * 健康检查
     */
    async healthCheck() {
        try {
            const response = await this.get('health/');
            console.log('✅ API健康检查通过:', response);
            return true;
        } catch (error) {
            console.error('❌ API健康检查失败:', error);
            return false;
        }
    }
}

// 创建全局实例
export const api = new SmartApiManager();

// 等待初始化完成
export const waitForApi = () => {
    return new Promise((resolve) => {
        const check = () => {
            if (api.baseURL) {
                resolve(api);
            } else {
                setTimeout(check, 100);
            }
        };
        check();
    });
};

// 全局错误处理
export const setupGlobalApiErrorHandler = () => {
    window.addEventListener('unhandledrejection', (event) => {
        if (event.reason && event.reason.message && 
            (event.reason.message.includes('fetch') || 
             event.reason.message.includes('NetworkError'))) {
            console.error('🌐 网络请求异常:', event.reason);
            
            // 显示用户友好的错误消息
            if (window.App && window.App.showToast) {
                window.App.showToast('网络连接异常，请检查后端服务');
            }
        }
    });
};

// 调试信息
export const getApiDebugInfo = () => ({
    baseURL: api.getBaseURL(),
    isDevelopment: api.isDevelopment(),
    currentLocation: window.location.href,
    savedConfig: localStorage.getItem('zmg_api_config')
});