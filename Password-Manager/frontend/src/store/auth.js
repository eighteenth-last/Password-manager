import { defineStore } from 'pinia'
import axios from '../utils/axios'
import router from '../router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
    tokenExpiry: localStorage.getItem('tokenExpiry') || null
  }),
  
  getters: {
    isLoggedIn: (state) => {
      return !!state.token && !!state.user && new Date(state.tokenExpiry) > new Date()
    },
    
    userEmail: (state) => {
      return state.user ? state.user.email : null
    }
  },
  
  actions: {
    async checkAuth() {
      // 如果有token但没有用户信息，尝试获取用户信息
      if (this.token && !this.user && new Date(this.tokenExpiry) > new Date()) {
        try {
          // 设置请求头
          axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
          
          // 获取用户信息
          const response = await axios.get('/api/user')
          this.user = response.data
          return true
        } catch (error) {
          console.error('获取用户信息失败:', error)
          this.logout()
          return false
        }
      }
      
      // 如果token过期，登出
      if (this.tokenExpiry && new Date(this.tokenExpiry) <= new Date()) {
        this.logout()
        return false
      }
      
      return this.isLoggedIn
    },
    
    async login(credentials) {
      try {
        const response = await axios.post('/api/login', credentials)
        
        // 保存token和用户信息
        this.token = response.data.token
        this.user = {
          id: response.data.user_id,
          email: response.data.email
        }
        
        // 计算token过期时间
        const expiresIn = response.data.expires_in || 86400 // 默认24小时
        const expiryDate = new Date(Date.now() + expiresIn * 1000)
        this.tokenExpiry = expiryDate.toISOString()
        
        // 保存到本地存储
        localStorage.setItem('token', this.token)
        localStorage.setItem('tokenExpiry', this.tokenExpiry)
        
        // 设置请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        return true
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },
    
    async register(userData) {
      try {
        const response = await axios.post('/api/register', userData)
        
        // 保存token和用户信息
        this.token = response.data.token
        this.user = {
          id: response.data.user_id,
          email: userData.email
        }
        
        // 计算token过期时间
        const expiresIn = response.data.expires_in || 86400 // 默认24小时
        const expiryDate = new Date(Date.now() + expiresIn * 1000)
        this.tokenExpiry = expiryDate.toISOString()
        
        // 保存到本地存储
        localStorage.setItem('token', this.token)
        localStorage.setItem('tokenExpiry', this.tokenExpiry)
        
        // 设置请求头
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
        
        return true
      } catch (error) {
        console.error('注册失败:', error)
        throw error
      }
    },
    
    logout() {
      // 清除状态
      this.user = null
      this.token = null
      this.tokenExpiry = null
      
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('tokenExpiry')
      
      // 清除请求头
      delete axios.defaults.headers.common['Authorization']
      
      // 重定向到登录页
      router.push({ name: 'login' })
    }
  }
})
