/**
 * API配置统一管理
 * 所有前端文件都应该使用这个配置来获取API地址
 */

// 延迟加载智能API管理器
let _api = null;

// 获取API实例（带缓存）
const getApi = async () => {
    if (_api) return _api;
    
    // 动态导入避免循环依赖
    const { api } = await import('../services/smartApi.js');
    _api = api;
    return api;
};

// 同步获取基础URL（用于不需要await的场景）
const getApiBaseUrlSync = () => {
    // 如果API已经初始化，直接返回
    if (window.__ZMG_API_BASE_URL__) {
        return window.__ZMG_API_BASE_URL__;
    }
    
    // 根据环境返回合适的默认值
    if (typeof window !== 'undefined') {
        // 浏览器环境
        if (window.location.port === '3000') {
            // Vite开发服务器，使用代理
            return '/api';
        } else if (window.location.port === '8001') {
            // 直接访问后端
            return '/api';
        } else {
            // 生产环境或其他端口
            return '/api';
        }
    }
    
    // Node.js环境或默认值
    return '/api';
};

// 导出配置对象
const apiConfig = {
    /**
     * 获取API基础URL
     * @returns {Promise<string>} API基础URL
     */
    getBaseURL: async () => {
        const api = await getApi();
        return api.getBaseURL();
    },
    
    /**
     * 同步获取API基础URL（不推荐，仅用于特殊情况）
     * @returns {string} API基础URL
     */
    getBaseURLSync: getApiBaseUrlSync,
    
    /**
     * 构建API完整URL
     * @param {string} endpoint - API端点
     * @returns {Promise<string>} 完整URL
     */
    buildUrl: async (endpoint) => {
        const api = await getApi();
        return api.buildUrl(endpoint);
    },
    
    /**
     * GET请求
     * @param {string} endpoint - API端点
     * @param {Object} options - 额外选项
     * @returns {Promise<any>} 响应数据
     */
    get: async (endpoint, options = {}) => {
        const api = await getApi();
        return api.get(endpoint, options);
    },
    
    /**
     * POST请求
     * @param {string} endpoint - API端点
     * @param {any} data - 请求数据
     * @param {Object} options - 额外选项
     * @returns {Promise<any>} 响应数据
     */
    post: async (endpoint, data, options = {}) => {
        const api = await getApi();
        return api.post(endpoint, data, options);
    },
    
    /**
     * PUT请求
     * @param {string} endpoint - API端点
     * @param {any} data - 请求数据
     * @param {Object} options - 额外选项
     * @returns {Promise<any>} 响应数据
     */
    put: async (endpoint, data, options = {}) => {
        const api = await getApi();
        return api.put(endpoint, data, options);
    },
    
    /**
     * DELETE请求
     * @param {string} endpoint - API端点
     * @param {Object} options - 额外选项
     * @returns {Promise<any>} 响应数据
     */
    delete: async (endpoint, options = {}) => {
        const api = await getApi();
        return api.delete(endpoint, options);
    },
    
    /**
     * 通用请求方法
     * @param {string} endpoint - API端点
     * @param {Object} options - fetch选项
     * @returns {Promise<any>} 响应数据
     */
    request: async (endpoint, options = {}) => {
        const api = await getApi();
        return api.request(endpoint, options);
    },
    
    /**
     * 健康检查
     * @returns {Promise<boolean>} 是否健康
     */
    healthCheck: async () => {
        const { api } = await import('../services/smartApi.js');
        return api.healthCheck();
    },
    
    /**
     * 等待API初始化完成
     * @returns {Promise} API实例
     */
    waitForReady: async () => {
        const { waitForApi } = await import('../services/smartApi.js');
        return waitForApi();
    },
    
    /**
     * 获取调试信息
     * @returns {Promise<Object>} 调试信息
     */
    getDebugInfo: async () => {
        const { getApiDebugInfo } = await import('../services/smartApi.js');
        return getApiDebugInfo();
    },
    
    /**
     * 手动设置API地址（用于特殊场景）
     * @param {string} baseURL - API基础URL
     */
    setBaseURL: async (baseURL) => {
        const { api } = await import('../services/smartApi.js');
        api.baseURL = baseURL;
        console.log('🔧 手动设置API地址:', baseURL);
    },
    
    /**
     * 强制重新发现API
     */
    rediscover: async () => {
        const { api } = await import('../services/smartApi.js');
        return api.rediscover();
    }
};

// 设置全局变量用于同步访问
setTimeout(async () => {
    try {
        const api = await getApi();
        window.__ZMG_API_BASE_URL__ = api.getBaseURL();
        console.log('🌐 API配置初始化完成:', window.__ZMG_API_BASE_URL__);
    } catch (error) {
        console.warn('⚠️ API配置初始化失败:', error);
        window.__ZMG_API_BASE_URL__ = '/api';
    }
}, 100);

// 导出默认配置
export default apiConfig;

// 为了向后兼容，也导出常用的常量
export const API_CONFIG = {
    VERSION: 'v1',
    TIMEOUT: 10000,
    RETRY_COUNT: 3
};