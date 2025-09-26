<template>
  <div class="settings-view">
    <h1 class="page-title">系统设置</h1>
    
    <!-- 账号信息卡片 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>账号信息</span>
        </div>
      </template>
      
      <div class="account-info">
        <div class="info-item">
          <span class="info-label">邮箱:</span>
          <span class="info-value">{{ userEmail }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">账号ID:</span>
          <span class="info-value">{{ userId }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">绑定账号数:</span>
          <span class="info-value">{{ bindingsCount }}</span>
        </div>
      </div>
      
      <div class="account-actions">
        <el-button type="danger" @click="confirmLogout">退出登录</el-button>
      </div>
    </el-card>
    
    <!-- 安全设置卡片 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>安全设置</span>
        </div>
      </template>
      
      <el-form
        ref="securityFormRef"
        :model="securityForm"
        label-width="140px"
      >
        <el-form-item label="自动锁定时间">
          <el-select v-model="securityForm.autoLockTimeout" style="width: 200px">
            <el-option label="1分钟" :value="1" />
            <el-option label="5分钟" :value="5" />
            <el-option label="15分钟" :value="15" />
            <el-option label="30分钟" :value="30" />
            <el-option label="1小时" :value="60" />
            <el-option label="从不" :value="0" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="securityForm.lockOnClose">关闭浏览器时锁定</el-checkbox>
        </el-form-item>
        
        <el-divider />
        
        <el-form-item label="修改主密码">
          <el-button type="primary" @click="showChangeMasterPasswordDialog">修改主密码</el-button>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveSecuritySettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 同步设置卡片 -->
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>同步设置</span>
        </div>
      </template>
      
      <el-form
        ref="syncFormRef"
        :model="syncForm"
        label-width="140px"
      >
        <el-form-item>
          <el-checkbox v-model="syncForm.autoSync">启用自动同步</el-checkbox>
        </el-form-item>
        
        <el-form-item label="同步间隔">
          <el-select v-model="syncForm.syncInterval" style="width: 200px" :disabled="!syncForm.autoSync">
            <el-option label="5分钟" :value="5" />
            <el-option label="15分钟" :value="15" />
            <el-option label="30分钟" :value="30" />
            <el-option label="1小时" :value="60" />
            <el-option label="6小时" :value="360" />
            <el-option label="12小时" :value="720" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="saveSyncSettings">保存设置</el-button>
          <el-button type="success" @click="syncNow" :loading="syncing">立即同步</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 危险区域卡片 -->
    <el-card class="settings-card danger-card">
      <template #header>
        <div class="card-header">
          <span>危险区域</span>
        </div>
      </template>
      
      <div class="danger-warning">
        <el-alert
          title="警告：以下操作将永久删除您的数据，无法恢复"
          type="error"
          :closable="false"
          show-icon
        />
      </div>
      
      <div class="danger-actions">
        <el-button type="danger" @click="confirmClearData">清除所有数据</el-button>
      </div>
    </el-card>
    
    <!-- 修改主密码对话框 -->
    <el-dialog
      v-model="changeMasterPasswordDialogVisible"
      title="修改主密码"
      width="500px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="120px"
      >
        <el-form-item label="当前主密码" prop="currentPassword">
          <el-input
            v-model="passwordForm.currentPassword"
            type="password"
            placeholder="请输入当前主密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="新主密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            placeholder="请输入新主密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认新主密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            placeholder="请再次输入新主密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="密码强度">
          <div class="password-strength">
            <div class="strength-meter">
              <div
                class="strength-bar"
                :class="passwordStrengthClass"
                :style="{ width: passwordStrengthWidth }"
              ></div>
            </div>
            <div class="strength-text">{{ passwordStrengthText }}</div>
          </div>
        </el-form-item>
        
        <div class="password-warning">
          <el-alert
            title="重要提示：请记住您的主密码！如果忘记，您将无法恢复已保存的密码。"
            type="warning"
            :closable="false"
            show-icon
          />
        </div>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="submitPasswordForm"
            :loading="submitting"
          >
            修改主密码
          </el-button>
          <el-button @click="changeMasterPasswordDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../../store/auth'
import { useBindingsStore } from '../../store/bindings'
import { usePasswordsStore } from '../../store/passwords'

const authStore = useAuthStore()
const bindingsStore = useBindingsStore()
const passwordsStore = usePasswordsStore()

// 状态
const syncing = ref(false)
const submitting = ref(false)
const changeMasterPasswordDialogVisible = ref(false)

// 账号信息
const userEmail = computed(() => authStore.userEmail || '未知')
const userId = computed(() => authStore.user?.id || '未知')
const bindingsCount = computed(() => bindingsStore.bindings.length || 0)

// 安全设置表单
const securityForm = ref({
  autoLockTimeout: 15,
  lockOnClose: true
})

// 同步设置表单
const syncForm = ref({
  autoSync: true,
  syncInterval: 15
})

// 修改主密码表单
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 表单验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.value.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前主密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新主密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少为8个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新主密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 表单引用
const securityFormRef = ref(null)
const syncFormRef = ref(null)
const passwordFormRef = ref(null)

// 密码强度计算
const passwordStrength = computed(() => {
  const password = passwordForm.value.newPassword
  if (!password) return 0
  
  let score = 0
  
  // 长度检查
  if (password.length >= 8) score++
  if (password.length >= 12) score++
  
  // 复杂性检查
  const hasLowercase = /[a-z]/.test(password)
  const hasUppercase = /[A-Z]/.test(password)
  const hasDigit = /\d/.test(password)
  const hasSpecial = /[^a-zA-Z0-9]/.test(password)
  
  if ((hasLowercase && hasUppercase) || (hasDigit && hasSpecial)) score++
  if (hasLowercase && hasUppercase && hasDigit && hasSpecial) score++
  
  return Math.min(3, score)
})

// 密码强度类
const passwordStrengthClass = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return 'weak'
  if (strength === 1) return 'medium'
  if (strength === 2) return 'strong'
  return 'very-strong'
})

// 密码强度宽度
const passwordStrengthWidth = computed(() => {
  const strength = passwordStrength.value
  return `${(strength + 1) * 25}%`
})

// 密码强度文本
const passwordStrengthText = computed(() => {
  const strength = passwordStrength.value
  if (strength === 0) return '弱'
  if (strength === 1) return '中'
  if (strength === 2) return '强'
  return '非常强'
})

// 监听密码变化，重新验证确认密码
watch(() => passwordForm.value.newPassword, () => {
  if (passwordForm.value.confirmPassword) {
    passwordFormRef.value?.validateField('confirmPassword')
  }
})

// 初始化
onMounted(async () => {
  try {
    // 加载绑定数据
    await bindingsStore.fetchBindings()
    
    // 加载设置
    loadSettings()
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  }
})

// 加载设置
const loadSettings = async () => {
  try {
    // 从本地存储中获取设置
    const settings = JSON.parse(localStorage.getItem('settings') || '{}')
    
    // 设置安全设置
    securityForm.value = {
      autoLockTimeout: settings.security?.autoLockTimeout || 15,
      lockOnClose: settings.security?.lockOnClose !== false
    }
    
    // 设置同步设置
    syncForm.value = {
      autoSync: settings.sync?.autoSync !== false,
      syncInterval: settings.sync?.syncInterval || 15
    }
  } catch (error) {
    console.error('加载设置失败:', error)
    // 使用默认设置
  }
}

// 保存安全设置
const saveSecuritySettings = async () => {
  try {
    // 从本地存储中获取设置
    const settings = JSON.parse(localStorage.getItem('settings') || '{}')
    
    // 更新安全设置
    settings.security = {
      autoLockTimeout: securityForm.value.autoLockTimeout,
      lockOnClose: securityForm.value.lockOnClose
    }
    
    // 保存到本地存储
    localStorage.setItem('settings', JSON.stringify(settings))
    
    ElMessage.success('安全设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败，请稍后重试')
  }
}

// 保存同步设置
const saveSyncSettings = async () => {
  try {
    // 从本地存储中获取设置
    const settings = JSON.parse(localStorage.getItem('settings') || '{}')
    
    // 更新同步设置
    settings.sync = {
      autoSync: syncForm.value.autoSync,
      syncInterval: syncForm.value.syncInterval
    }
    
    // 保存到本地存储
    localStorage.setItem('settings', JSON.stringify(settings))
    
    ElMessage.success('同步设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    ElMessage.error('保存设置失败，请稍后重试')
  }
}

// 立即同步
const syncNow = async () => {
  syncing.value = true
  try {
    await passwordsStore.syncPasswords()
    ElMessage.success('同步成功')
  } catch (error) {
    console.error('同步失败:', error)
    ElMessage.error('同步失败，请稍后重试')
  } finally {
    syncing.value = false
  }
}

// 显示修改主密码对话框
const showChangeMasterPasswordDialog = () => {
  // 重置表单
  passwordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  
  changeMasterPasswordDialogVisible.value = true
}

// 提交密码表单
const submitPasswordForm = async () => {
  if (!passwordFormRef.value) return
  
  try {
    // 表单验证
    await passwordFormRef.value.validate()
    
    // 检查密码强度
    if (passwordStrength.value < 2) {
      ElMessage.warning('请设置更强的密码')
      return
    }
    
    // 设置提交状态
    submitting.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 关闭对话框
    changeMasterPasswordDialogVisible.value = false
    
    // 显示成功消息
    ElMessage.success('主密码已修改')
  } catch (error) {
    console.error('修改主密码失败:', error)
    ElMessage.error('修改主密码失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// 确认退出登录
const confirmLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    authStore.logout()
  }).catch(() => {})
}

// 确认清除数据
const confirmClearData = () => {
  ElMessageBox.prompt(
    '此操作将永久删除您的所有数据，无法恢复。请输入"DELETE"以确认。',
    '危险操作',
    {
      confirmButtonText: '清除数据',
      cancelButtonText: '取消',
      inputPattern: /^DELETE$/,
      inputErrorMessage: '请输入"DELETE"以确认',
      type: 'error'
    }
  ).then(({ value }) => {
    if (value === 'DELETE') {
      clearAllData()
    }
  }).catch(() => {})
}

// 清除所有数据
const clearAllData = async () => {
  try {
    // 清除本地存储
    localStorage.clear()
    
    // 清除状态
    passwordsStore.$reset()
    bindingsStore.$reset()
    
    // 退出登录
    authStore.logout()
    
    ElMessage.success('所有数据已清除')
  } catch (error) {
    console.error('清除数据失败:', error)
    ElMessage.error('清除数据失败，请稍后重试')
  }
}
</script>

<style scoped>
.settings-view {
  padding: 20px;
}

.settings-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.account-info {
  margin-bottom: 20px;
}

.info-item {
  margin-bottom: 10px;
  display: flex;
}

.info-label {
  width: 120px;
  font-weight: 500;
  color: #606266;
}

.info-value {
  flex: 1;
}

.account-actions {
  margin-top: 20px;
}

.danger-card {
  border: 1px solid #F56C6C;
}

.danger-warning {
  margin-bottom: 20px;
}

.danger-actions {
  margin-top: 20px;
}

.password-strength {
  margin-top: 10px;
}

.strength-meter {
  height: 5px;
  background-color: #eee;
  border-radius: 2px;
  margin-bottom: 5px;
}

.strength-bar {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s, background-color 0.3s;
}

.strength-bar.weak {
  background-color: #F56C6C;
}

.strength-bar.medium {
  background-color: #E6A23C;
}

.strength-bar.strong {
  background-color: #67C23A;
}

.strength-bar.very-strong {
  background-color: #409EFF;
}

.strength-text {
  font-size: 12px;
  color: #909399;
  text-align: right;
}

.password-warning {
  margin: 15px 0;
}
</style>
