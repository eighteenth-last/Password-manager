<template>
  <div class="dashboard-home">
    <h1 class="page-title">仪表盘</h1>
    
    <el-row :gutter="20">
      <!-- 密码统计卡片 -->
      <el-col :span="8">
        <el-card class="stat-card">
          <template #header>
            <div class="card-header">
              <span>密码统计</span>
              <el-button type="text" @click="refreshStats">
                <el-icon><el-icon-refresh /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-item">
              <div class="stat-value">{{ stats.totalPasswords }}</div>
              <div class="stat-label">总密码数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.totalDomains }}</div>
              <div class="stat-label">网站数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ stats.sharedPasswords }}</div>
              <div class="stat-label">共享密码</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 最近活动卡片 -->
      <el-col :span="8">
        <el-card class="stat-card">
          <template #header>
            <div class="card-header">
              <span>同步状态</span>
              <el-button type="text" @click="syncPasswords" :loading="syncing">
                <el-icon><el-icon-upload /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="card-content">
            <div class="sync-status">
              <div class="status-icon" :class="{ synced: isSynced }">
                <el-icon v-if="isSynced"><el-icon-check /></el-icon>
                <el-icon v-else><el-icon-warning /></el-icon>
              </div>
              <div class="status-info">
                <div class="status-text">{{ syncStatusText }}</div>
                <div class="status-time">{{ lastSyncTime }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <!-- 绑定账号卡片 -->
      <el-col :span="8">
        <el-card class="stat-card">
          <template #header>
            <div class="card-header">
              <span>账号绑定</span>
              <el-button type="text" @click="goToBindings">
                <el-icon><el-icon-more /></el-icon>
              </el-button>
            </div>
          </template>
          <div class="card-content">
            <div v-if="bindings.length > 0">
              <div class="binding-item" v-for="binding in displayBindings" :key="binding.id">
                <el-avatar size="small" :src="binding.avatar">
                  {{ binding.bound_account_email.charAt(0).toUpperCase() }}
                </el-avatar>
                <span class="binding-email">{{ binding.bound_account_email }}</span>
                <el-tag size="small" :type="binding.permissions === 'read' ? 'info' : 'warning'">
                  {{ binding.permissions === 'read' ? '只读' : '读写' }}
                </el-tag>
              </div>
              <div v-if="bindings.length > 3" class="binding-more">
                还有 {{ bindings.length - 3 }} 个绑定账号...
              </div>
            </div>
            <div v-else class="empty-bindings">
              <el-empty description="暂无绑定账号" :image-size="60">
                <el-button type="primary" size="small" @click="goToBindings">
                  绑定账号
                </el-button>
              </el-empty>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快捷操作卡片 -->
    <el-card class="action-card">
      <template #header>
        <div class="card-header">
          <span>快捷操作</span>
        </div>
      </template>
      <div class="quick-actions">
        <el-button type="primary" @click="goToAddPassword">
          <el-icon><el-icon-plus /></el-icon>
          添加密码
        </el-button>
        <el-button type="success" @click="goToPasswords">
          <el-icon><el-icon-document /></el-icon>
          管理密码
        </el-button>
        <el-button type="warning" @click="goToBindings">
          <el-icon><el-icon-connection /></el-icon>
          账号绑定
        </el-button>
        <el-button type="info" @click="goToSettings">
          <el-icon><el-icon-setting /></el-icon>
          系统设置
        </el-button>
      </div>
    </el-card>
    
    <!-- 最近密码卡片 -->
    <el-card class="password-card">
      <template #header>
        <div class="card-header">
          <span>最近密码</span>
          <el-button type="text" @click="goToPasswords">
            查看全部
          </el-button>
        </div>
      </template>
      <div v-loading="loading">
        <el-table
          :data="recentPasswords"
          style="width: 100%"
          v-if="recentPasswords.length > 0"
        >
          <el-table-column prop="domain" label="网站" width="180">
            <template #default="scope">
              <div class="domain-cell">
                <div class="domain-icon">{{ scope.row.domain.charAt(0).toUpperCase() }}</div>
                <span>{{ scope.row.domain }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="username" label="用户名" />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button
                size="small"
                @click="copyPassword(scope.row)"
                type="primary"
                plain
              >
                复制密码
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无密码记录" :image-size="100" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { usePasswordsStore } from '../../store/passwords'
import { useBindingsStore } from '../../store/bindings'
import {
  Refresh as ElIconRefresh,
  Upload as ElIconUpload,
  Check as ElIconCheck,
  Warning as ElIconWarning,
  More as ElIconMore,
  Plus as ElIconPlus,
  Document as ElIconDocument,
  Connection as ElIconConnection,
  Setting as ElIconSetting
} from '@element-plus/icons-vue'

const router = useRouter()
const passwordsStore = usePasswordsStore()
const bindingsStore = useBindingsStore()

// 加载状态
const loading = ref(true)
const syncing = ref(false)

// 统计数据
const stats = ref({
  totalPasswords: 0,
  totalDomains: 0,
  sharedPasswords: 0
})

// 最近密码
const recentPasswords = ref([])

// 绑定账号
const bindings = ref([])

// 显示的绑定账号（最多3个）
const displayBindings = computed(() => {
  return bindings.value.slice(0, 3)
})

// 同步状态
const isSynced = computed(() => {
  return !!passwordsStore.lastSyncTime
})

// 同步状态文本
const syncStatusText = computed(() => {
  return isSynced.value ? '已同步' : '未同步'
})

// 最后同步时间
const lastSyncTime = computed(() => {
  if (!passwordsStore.lastSyncTime) return '从未同步'
  
  const lastSync = new Date(passwordsStore.lastSyncTime)
  return lastSync.toLocaleString()
})

// 初始化
onMounted(async () => {
  try {
    // 加载密码数据
    await loadData()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
})

// 加载数据
const loadData = async () => {
  // 加载密码
  await passwordsStore.fetchPasswords()
  
  // 加载共享密码
  await passwordsStore.fetchSharedPasswords()
  
  // 加载绑定关系
  const bindingData = await bindingsStore.fetchBindings()
  bindings.value = bindingData.bindings
  
  // 更新统计数据
  updateStats()
  
  // 更新最近密码
  updateRecentPasswords()
}

// 更新统计数据
const updateStats = () => {
  const domains = new Set()
  passwordsStore.passwords.forEach(password => {
    domains.add(password.domain)
  })
  
  stats.value = {
    totalPasswords: passwordsStore.passwords.length,
    totalDomains: domains.size,
    sharedPasswords: passwordsStore.sharedPasswords.length
  }
}

// 更新最近密码
const updateRecentPasswords = () => {
  // 按更新时间排序，取最近的5个
  recentPasswords.value = [...passwordsStore.passwords]
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    .slice(0, 5)
}

// 刷新统计数据
const refreshStats = async () => {
  loading.value = true
  try {
    await loadData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    console.error('刷新数据失败:', error)
    ElMessage.error('刷新数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 同步密码
const syncPasswords = async () => {
  syncing.value = true
  try {
    await passwordsStore.syncPasswords()
    updateStats()
    updateRecentPasswords()
    ElMessage.success('同步成功')
  } catch (error) {
    console.error('同步失败:', error)
    ElMessage.error('同步失败，请稍后重试')
  } finally {
    syncing.value = false
  }
}

// 复制密码
const copyPassword = (password) => {
  // 在实际应用中，这里应该调用解密逻辑
  // 此处模拟复制密码
  ElMessage.success(`已复制 ${password.domain} 的密码`)
}

// 导航方法
const goToAddPassword = () => {
  router.push('/dashboard/passwords?action=add')
}

const goToPasswords = () => {
  router.push('/dashboard/passwords')
}

const goToBindings = () => {
  router.push('/dashboard/bindings')
}

const goToSettings = () => {
  router.push('/dashboard/settings')
}
</script>

<style scoped>
.dashboard-home {
  padding: 20px;
}

.stat-card {
  margin-bottom: 20px;
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  padding: 10px 0;
}

.stat-item {
  text-align: center;
  padding: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: 500;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.sync-status {
  display: flex;
  align-items: center;
  padding: 10px;
}

.status-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #F56C6C;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
}

.status-icon.synced {
  background-color: #67C23A;
}

.status-info {
  flex: 1;
}

.status-text {
  font-size: 16px;
  font-weight: 500;
}

.status-time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.binding-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #eee;
}

.binding-item:last-child {
  border-bottom: none;
}

.binding-email {
  flex: 1;
  margin: 0 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.binding-more {
  text-align: center;
  padding: 8px 0;
  color: #909399;
  font-size: 12px;
}

.empty-bindings {
  padding: 20px 0;
}

.action-card {
  margin-bottom: 20px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.password-card {
  margin-bottom: 20px;
}

.domain-cell {
  display: flex;
  align-items: center;
}

.domain-icon {
  width: 30px;
  height: 30px;
  border-radius: 4px;
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-weight: bold;
}
</style>
