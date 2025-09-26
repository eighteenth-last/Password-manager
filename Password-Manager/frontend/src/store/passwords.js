import { defineStore } from 'pinia'
import axios from '../utils/axios'

export const usePasswordsStore = defineStore('passwords', {
  state: () => ({
    passwords: [],
    sharedPasswords: [],
    loading: false,
    error: null,
    lastSyncTime: null
  }),
  
  getters: {
    getPasswordsByDomain: (state) => {
      return (domain) => {
        return state.passwords.filter(password => password.domain === domain)
      }
    },
    
    getPasswordById: (state) => {
      return (id) => {
        return state.passwords.find(password => password.id === id)
      }
    },
    
    getSharedPasswordsByDomain: (state) => {
      return (domain) => {
        return state.sharedPasswords.filter(password => password.domain === domain)
      }
    },
    
    domains: (state) => {
      const domains = new Set()
      state.passwords.forEach(password => domains.add(password.domain))
      return Array.from(domains).sort()
    },
    
    sharedDomains: (state) => {
      const domains = new Set()
      state.sharedPasswords.forEach(password => domains.add(password.domain))
      return Array.from(domains).sort()
    }
  },
  
  actions: {
    // 通用的API请求处理方法
    async _handleApiRequest(apiCall, errorMessage = '操作失败') {
      this.loading = true
      this.error = null
      
      try {
        const result = await apiCall()
        return result
      } catch (error) {
        console.error(`${errorMessage}:`, error)
        this.error = error.response?.data?.message || errorMessage
        throw error
      } finally {
        this.loading = false
      }
    },

    // 参数验证辅助方法
    _validatePasswordIds(passwordIds) {
      if (!Array.isArray(passwordIds)) {
        throw new Error('密码ID必须是数组格式')
      }
      if (passwordIds.length === 0) {
        throw new Error('密码ID列表不能为空')
      }
      if (passwordIds.some(id => !id || (typeof id !== 'string' && typeof id !== 'number'))) {
        throw new Error('密码ID格式无效')
      }
    },

    async fetchPasswords() {
      return this._handleApiRequest(async () => {
        const response = await axios.get('/api/passwords')
        this.passwords = response.data.passwords || []
        return this.passwords
      }, '获取密码失败')
    },
    
    async fetchSharedPasswords() {
      return this._handleApiRequest(async () => {
        const response = await axios.get('/api/passwords/shared')
        this.sharedPasswords = response.data.sharedPasswords || []
        return this.sharedPasswords
      }, '获取共享密码失败')
    },
    
    async addPassword(passwordData) {
      if (!passwordData || typeof passwordData !== 'object') {
        throw new Error('密码数据格式无效')
      }
      
      return this._handleApiRequest(async () => {
        const response = await axios.post('/api/passwords', passwordData)
        
        // 添加新密码到列表
        if (response.data.password) {
          this.passwords.push(response.data.password)
        }
        
        return response.data.password
      }, '添加密码失败')
    },
    
    async updatePassword(passwordId, passwordData) {
      if (!passwordId) {
        throw new Error('密码ID不能为空')
      }
      if (!passwordData || typeof passwordData !== 'object') {
        throw new Error('密码数据格式无效')
      }
      
      return this._handleApiRequest(async () => {
        const response = await axios.put(`/api/passwords/${passwordId}`, passwordData)
        
        // 更新列表中的密码
        if (response.data.password) {
          const index = this.passwords.findIndex(p => p.id === passwordId)
          if (index !== -1) {
            this.passwords[index] = response.data.password
          }
        }
        
        return response.data.password
      }, '更新密码失败')
    },
    
    async deletePassword(passwordId) {
      if (!passwordId) {
        throw new Error('密码ID不能为空')
      }
      
      return this._handleApiRequest(async () => {
        await axios.delete(`/api/passwords/${passwordId}`)
        
        // 从列表中移除密码
        this.passwords = this.passwords.filter(p => p.id !== passwordId)
        
        return true
      }, '删除密码失败')
    },

    async batchDeletePasswords(passwordIds) {
      // 参数验证
      this._validatePasswordIds(passwordIds)
      
      return this._handleApiRequest(async () => {
        const response = await axios.post('/api/batch_delete', {
          password_ids: passwordIds
        })
        
        // 优化：只有在服务器确认删除成功时才更新本地状态
        const { deletedCount = 0, failedCount = 0, failedDetails = [] } = response.data
        
        if (deletedCount > 0) {
          // 从列表中移除已成功删除的密码
          // 如果有失败的情况，需要更精确地处理
          if (failedCount === 0) {
            // 全部成功，直接过滤
            this.passwords = this.passwords.filter(p => !passwordIds.includes(p.id))
          } else {
            // 部分成功，需要根据失败详情来精确移除
            const failedIds = this._extractFailedIds(failedDetails, passwordIds)
            const successIds = passwordIds.filter(id => !failedIds.includes(id))
            this.passwords = this.passwords.filter(p => !successIds.includes(p.id))
          }
        }
        
        return {
          deletedCount,
          failedCount,
          failedDetails,
          message: this._generateBatchDeleteMessage(deletedCount, failedCount)
        }
      }, '批量删除密码失败')
    },

    // 辅助方法：从失败详情中提取失败的ID
    _extractFailedIds(failedDetails, originalIds) {
      const failedIds = []
      failedDetails.forEach(detail => {
        // 尝试从错误信息中提取ID
        const match = detail.match(/密码记录不存在: (\w+)|无权删除密码: (\w+)|删除失败: (\w+)/)
        if (match) {
          const failedId = match[1] || match[2] || match[3]
          if (originalIds.includes(failedId)) {
            failedIds.push(failedId)
          }
        }
      })
      return failedIds
    },

    // 辅助方法：生成批量删除结果消息
    _generateBatchDeleteMessage(deletedCount, failedCount) {
      if (failedCount === 0) {
        return `成功删除 ${deletedCount} 个密码`
      } else if (deletedCount === 0) {
        return `删除失败，${failedCount} 个密码无法删除`
      } else {
        return `部分成功：删除了 ${deletedCount} 个密码，${failedCount} 个密码删除失败`
      }
    },
    
    async syncPasswords() {
      return this._handleApiRequest(async () => {
        // 同步本地密码到服务器
        const response = await axios.post('/api/passwords/sync', {
          passwords: this.passwords
        })
        
        // 更新本地密码列表
        if (response.data.serverPasswords) {
          this.passwords = response.data.serverPasswords
        }
        
        // 更新同步时间
        this.lastSyncTime = new Date().toISOString()
        
        return this.passwords
      }, '同步密码失败')
    },
    
    async syncSharedPasswords() {
      return this._handleApiRequest(async () => {
        // 同步本地共享密码到服务器
        const response = await axios.post('/api/passwords/shared/sync', {
          passwords: this.sharedPasswords
        })
        
        // 更新本地共享密码列表
        if (response.data.sharedPasswords) {
          this.sharedPasswords = response.data.sharedPasswords
        }
        
        return this.sharedPasswords
      }, '同步共享密码失败')
    },
    
    async updateSharedPassword(passwordId, passwordData) {
      if (!passwordId) {
        throw new Error('密码ID不能为空')
      }
      if (!passwordData || typeof passwordData !== 'object') {
        throw new Error('密码数据格式无效')
      }
      
      return this._handleApiRequest(async () => {
        const response = await axios.put(`/api/passwords/shared/${passwordId}`, passwordData)
        
        // 更新列表中的共享密码
        if (response.data.password) {
          const index = this.sharedPasswords.findIndex(p => p.id === passwordId)
          if (index !== -1) {
            this.sharedPasswords[index] = response.data.password
          }
        }
        
        return response.data.password
      }, '更新共享密码失败')
    },
    
    async importPasswords(passwordsArray, forceImport = false) {
      if (!Array.isArray(passwordsArray)) {
        throw new Error('密码数据必须是数组格式')
      }
      if (passwordsArray.length === 0) {
        throw new Error('密码数据不能为空')
      }
      
      return this._handleApiRequest(async () => {
        // 导入密码
        const response = await axios.post('/api/txt_import', {
          passwords: passwordsArray,
          forceImport: forceImport
        })
        
        // 更新密码列表
        if (response.data.importedPasswords) {
          // 添加新导入的密码到本地列表
          this.passwords = [...this.passwords, ...response.data.importedPasswords]
        }
        
        return {
          importedCount: response.data.importedCount || 0,
          skippedCount: response.data.skippedCount || 0,
          skippedDetails: response.data.skippedDetails || [],
          errors: response.data.errors || []
        }
      }, '导入密码失败')
    },

    async importCSVPasswords(file, forceImport = false) {
      if (!file) {
        throw new Error('文件不能为空')
      }
      
      return this._handleApiRequest(async () => {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('forceImport', forceImport)
        
        const response = await axios.post('/api/csv_import', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        // 更新密码列表
        if (response.data.importedPasswords) {
          this.passwords = [...this.passwords, ...response.data.importedPasswords]
        }
        
        return {
          importedCount: response.data.importedCount || 0,
          skippedCount: response.data.skippedCount || 0,
          skippedDetails: response.data.skippedDetails || [],
          errors: response.data.errors || []
        }
      }, '导入CSV密码失败')
    },

    // 清除错误状态
    clearError() {
      this.error = null
    },

    // 重置loading状态（用于异常情况）
    resetLoading() {
      this.loading = false
    }
  }
})