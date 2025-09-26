import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const instance = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // 允许跨域请求时发送凭证
})

// 请求拦截器
instance.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
instance.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('响应错误:', error)
    
    // 处理错误响应
    if (error.response) {
      // 服务器返回错误状态码
      const status = error.response.status
      const message = error.response.data?.message || '请求失败'
      
      // 处理401未授权错误
      if (status === 401) {
        // 清除token
        localStorage.removeItem('token')
        localStorage.removeItem('tokenExpiry')
        
        // 重定向到登录页
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
      
      // 显示错误消息
      ElMessage.error(message)
    } else if (error.request) {
      // 请求发送但没有收到响应
      ElMessage.error('服务器无响应，请稍后重试')
    } else {
      // 请求设置时发生错误
      ElMessage.error('请求失败，请稍后重试')
    }
    
    return Promise.reject(error)
  }
)

export default instance
