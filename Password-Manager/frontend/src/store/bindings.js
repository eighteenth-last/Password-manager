import { defineStore } from 'pinia'
import axios from '../utils/axios'

export const useBindingsStore = defineStore('bindings', {
  state: () => ({
    bindings: [],
    pendingRequests: [],
    loading: false,
    error: null
  }),
  
  getters: {
    getBindingById: (state) => {
      return (id) => {
        return state.bindings.find(binding => binding.id === id)
      }
    },
    
    getRequestById: (state) => {
      return (id) => {
        return state.pendingRequests.find(request => request.id === id)
      }
    },
    
    hasBindings: (state) => {
      return state.bindings.length > 0
    },
    
    hasPendingRequests: (state) => {
      return state.pendingRequests.length > 0
    }
  },
  
  actions: {
    async fetchBindings() {
      this.loading = true
      this.error = null
      
      try {
        // 获取绑定关系和待处理请求
        const response = await axios.get('/api/accounts/bindings')
        this.bindings = response.data.bindings || []
        this.pendingRequests = response.data.pendingRequests || []
        return {
          bindings: this.bindings,
          pendingRequests: this.pendingRequests
        }
      } catch (error) {
        console.error('获取绑定关系失败:', error)
        this.error = error.response?.data?.message || '获取绑定关系失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async bindAccount(targetEmail) {
      this.loading = true
      this.error = null
      
      try {
        // 发送绑定请求
        const response = await axios.post('/api/accounts/bind', { targetEmail })
        return response.data
      } catch (error) {
        console.error('发送绑定请求失败:', error)
        this.error = error.response?.data?.message || '发送绑定请求失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async acceptBindingRequest(bindingId) {
      this.loading = true
      this.error = null
      
      try {
        // 接受绑定请求
        await axios.post(`/api/accounts/bindings/${bindingId}/accept`)
        
        // 更新本地数据
        const request = this.getRequestById(bindingId)
        if (request) {
          // 从待处理请求中移除
          this.pendingRequests = this.pendingRequests.filter(r => r.id !== bindingId)
          
          // 添加到活动绑定列表
          this.bindings.push({
            ...request,
            binding_status: 'active'
          })
        }
        
        return true
      } catch (error) {
        console.error('接受绑定请求失败:', error)
        this.error = error.response?.data?.message || '接受绑定请求失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async rejectBindingRequest(bindingId) {
      this.loading = true
      this.error = null
      
      try {
        // 拒绝绑定请求
        await axios.post(`/api/accounts/bindings/${bindingId}/reject`)
        
        // 从待处理请求中移除
        this.pendingRequests = this.pendingRequests.filter(r => r.id !== bindingId)
        
        return true
      } catch (error) {
        console.error('拒绝绑定请求失败:', error)
        this.error = error.response?.data?.message || '拒绝绑定请求失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async unbindAccount(bindingId) {
      this.loading = true
      this.error = null
      
      try {
        // 解除绑定
        await axios.delete(`/api/accounts/bindings/${bindingId}`)
        
        // 从绑定列表中移除
        this.bindings = this.bindings.filter(b => b.id !== bindingId)
        
        return true
      } catch (error) {
        console.error('解除绑定失败:', error)
        this.error = error.response?.data?.message || '解除绑定失败'
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async updateBindingPermissions(bindingId, permissions) {
      this.loading = true
      this.error = null
      
      try {
        // 更新绑定权限
        await axios.put(`/api/accounts/bindings/${bindingId}/permissions`, { permissions })
        
        // 更新本地数据
        const binding = this.getBindingById(bindingId)
        if (binding) {
          binding.permissions = permissions
        }
        
        return true
      } catch (error) {
        console.error('更新绑定权限失败:', error)
        this.error = error.response?.data?.message || '更新绑定权限失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
})
