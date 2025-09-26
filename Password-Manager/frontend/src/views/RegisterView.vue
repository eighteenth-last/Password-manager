<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <div class="logo">🔒</div>
        <h1>密码管家</h1>
        <p>创建管理员账号</p>
      </div>
      
  <el-form
    ref="registerFormRef"
    :model="registerForm"
    :rules="registerRules"
    label-position="top"
    @submit.prevent="handleRegister"
  >
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
            type="email"
            autocomplete="email"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            placeholder="请输入密码"
            type="password"
            autocomplete="new-password"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            placeholder="请再次输入密码"
            type="password"
            autocomplete="new-password"
            show-password
          />
        </el-form-item>
        
        <div class="password-strength">
          <div class="strength-label">密码强度:</div>
          <div class="strength-meter">
            <div
              class="strength-bar"
              :class="passwordStrengthClass"
              :style="{ width: passwordStrengthWidth }"
            ></div>
          </div>
          <div class="strength-text">{{ passwordStrengthText }}</div>
        </div>
        
        <div class="form-actions">
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            :disabled="loading"
            class="submit-btn"
          >
            注册
          </el-button>
        </div>
      </el-form>
      
      <div class="register-footer">
        <p>
          已有账号？
          <router-link to="/login">立即登录</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

// 注册表单
const registerForm = reactive({
  email: '',
  password: '',
  confirmPassword: ''
})

// 密码强度计算
const passwordStrength = computed(() => {
  const password = registerForm.password
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

// 表单验证规则
const validateConfirmPassword = (rule, value, callback) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少为8个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 监听密码变化，重新验证确认密码
watch(() => registerForm.password, () => {
  if (registerForm.confirmPassword) {
    registerFormRef.value?.validateField('confirmPassword')
  }
})

// 注册表单引用
const registerFormRef = ref(null)

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    // 表单验证
    await registerFormRef.value.validate()
    
    // 检查密码强度
    if (passwordStrength.value < 2) {
      ElMessage.warning('请设置更强的密码')
      return
    }
    
    // 设置加载状态
    loading.value = true
    
    // 调用注册接口
    await authStore.register({
      email: registerForm.email,
      password: registerForm.password
    })
    
    // 注册成功提示
    ElMessage.success('注册成功')
    
    // 重定向到仪表盘
    router.push('/dashboard')
  } catch (error) {
    console.error('注册失败:', error)
    ElMessage.error(error.response?.data?.message || '注册失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 400px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.logo {
  font-size: 48px;
  margin-bottom: 10px;
}

.register-header h1 {
  font-size: 24px;
  font-weight: 500;
  margin-bottom: 10px;
  color: #409EFF;
}

.register-header p {
  font-size: 14px;
  color: #909399;
}

.password-strength {
  margin-top: 10px;
  margin-bottom: 20px;
}

.strength-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 5px;
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

.form-actions {
  margin-top: 30px;
}

.submit-btn {
  width: 100%;
}

.register-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.register-footer a {
  color: #409EFF;
  text-decoration: none;
}

.register-footer a:hover {
  text-decoration: underline;
}
</style>
