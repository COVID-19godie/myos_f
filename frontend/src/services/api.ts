import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

// 请求拦截器自动注入 Token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器处理认证错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.reload()
    }
    return Promise.reject(error)
  }
)

export const desktopApi = {
  // 获取桌面图标
  getIcons: (parentId = 'root') => api.get(`/desktop/?parent_id=${parentId}`),
  
  // 移动图标
  moveIcon: (id: number, data: {x: number, y: number, parent_id?: any}) => 
    api.patch(`/desktop/${id}/move/`, data),
  
  // 重命名图标
  renameIcon: (id: number, data: {name: string}) => 
    api.post(`/desktop/${id}/rename/`, data),
  
  // 删除图标
  deleteIcon: (id: number) => 
    api.delete(`/desktop/${id}/uninstall/`),
  
  // 创建文件夹
  createFolder: (data: {name: string, x: number, y: number}) => 
    api.post('/desktop/create_folder/', data),
  
  // 文件上传
  uploadFile: (formData: FormData) => 
    api.post('/desktop/upload_file/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  // 获取分类列表
  getCategories: () => api.get('/categories/'),
  
  // 安装H5应用
  installH5App: (formData: FormData) => 
    api.post('/desktop/install_h5_app/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  
  // 登录
  login: (username: string, password: string) => 
    api.post('/token/', { username, password })
}

export default api