<template>
  <div class="passwords-view">
    <div class="page-header">
      <h1 class="page-title">密码管理</h1>
      <el-button type="primary" @click="showAddPasswordDialog">
        <el-icon><el-icon-plus /></el-icon>
        添加密码
      </el-button>
    </div>
    
    <!-- 搜索和筛选 -->
    <div class="filter-section">
      <el-card class="filter-card" shadow="hover">
        <div class="filter-header">
          <h3 class="filter-title">
            <el-icon class="filter-icon"><el-icon-search /></el-icon>
            筛选与操作
          </h3>
        </div>
        
        <el-row :gutter="16" class="filter-content">
          <el-col :span="6">
            <div class="filter-item">
              <label class="filter-label">搜索密码</label>
              <el-input
                v-model="searchQuery"
                placeholder="搜索网站或用户名"
                clearable
                prefix-icon="el-icon-search"
                @input="filterPasswords"
                class="search-input"
              />
            </div>
          </el-col>
          
          <el-col :span="6">
            <div class="filter-item">
              <label class="filter-label">选择网站</label>
              <el-select
                v-model="selectedDomain"
                placeholder="选择网站"
                clearable
                style="width: 100%"
                @change="filterPasswords"
                class="domain-select"
              >
                <el-option
                  v-for="domain in domains"
                  :key="domain"
                  :label="domain"
                  :value="domain"
                />
              </el-select>
            </div>
          </el-col>
          
          <el-col :span="12">
            <div class="filter-item">
              <label class="filter-label">操作</label>
              <div class="action-buttons">
                <el-button @click="refreshPasswords" :loading="loading" class="action-btn">
                  <el-icon><el-icon-refresh /></el-icon>
                  刷新
                </el-button>
                <el-button type="success" @click="syncPasswords" :loading="syncing" class="action-btn">
                  <el-icon><el-icon-upload /></el-icon>
                  同步
                </el-button>
                <el-button type="primary" @click="showImportDialog" :loading="importing" class="action-btn">
                  <el-icon><el-icon-download /></el-icon>
                  导入TXT
                </el-button>
                <el-button type="info" @click="showBrowserImportDialog" :loading="importing" class="action-btn">
                  <el-icon><el-icon-document /></el-icon>
                  浏览器导入
                </el-button>
                <el-button 
                  type="danger" 
                  @click="confirmBatchDelete" 
                  :disabled="selectedPasswords.length === 0"
                  :loading="batchDeleting"
                  class="action-btn batch-delete-btn"
                >
                  <el-icon><el-icon-delete /></el-icon>
                  批量删除 ({{ selectedPasswords.length }})
                </el-button>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>
    
    <!-- 密码列表 -->
    <el-card v-loading="loading" class="password-list-card">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="我的密码" name="my">
          <el-table
            :data="filteredPasswords"
            style="width: 100%"
            v-if="filteredPasswords.length > 0"
            @selection-change="handleSelectionChange"
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="domain" label="网站名称" width="180">
              <template #default="scope">
                <div class="domain-cell">
                  <div class="domain-icon">{{ scope.row.domain.charAt(0).toUpperCase() }}</div>
                  <span>{{ scope.row.domain }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="encrypted_username" label="用户名">
              <template #default="scope">
                {{ scope.row.encrypted_username }}
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.updated_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250">
              <template #default="scope">
                <el-button
                  size="small"
                  @click="copyPassword(scope.row)"
                  type="primary"
                  plain
                >
                  复制密码
                </el-button>
                <el-button
                  size="small"
                  @click="editPassword(scope.row)"
                  type="info"
                  plain
                >
                  编辑
                </el-button>
                <el-button
                  size="small"
                  @click="confirmDeletePassword(scope.row)"
                  type="danger"
                  plain
                >
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="没有找到密码记录" />
        </el-tab-pane>
        
        <el-tab-pane label="共享密码" name="shared">
          <el-table
            :data="filteredSharedPasswords"
            style="width: 100%"
            v-if="filteredSharedPasswords.length > 0"
          >
            <el-table-column prop="domain" label="网站名称" width="180">
              <template #default="scope">
                <div class="domain-cell">
                  <div class="domain-icon">{{ scope.row.domain.charAt(0).toUpperCase() }}</div>
                  <span>{{ scope.row.domain }}</span>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="encrypted_username" label="用户名">
              <template #default="scope">
                {{ scope.row.encrypted_username }}
              </template>
            </el-table-column>
            <el-table-column prop="owner_email" label="共享者" width="180" />
            <el-table-column label="权限" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.permissions === 'read' ? 'info' : 'warning'">
                  {{ scope.row.permissions === 'read' ? '只读' : '读写' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button
                  size="small"
                  @click="copyPassword(scope.row)"
                  type="primary"
                  plain
                >
                  复制密码
                </el-button>
                <el-button
                  v-if="scope.row.permissions === 'write'"
                  size="small"
                  @click="editSharedPassword(scope.row)"
                  type="info"
                  plain
                >
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="没有共享的密码记录" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
    <!-- 浏览器导入对话框 -->
    <BrowserImportDialog
        v-model:visible="browserImportDialogVisible"
        @imported="onImportSuccess"
    />

    <!-- 导入TXT文件对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="导入密码文件"
      width="500px"
    >
      <div class="import-dialog-content">
        <p>请选择TXT格式的密码文件进行导入。支持以下文件格式：</p>
        <pre>
            格式一：
            平台名称:
            账户: 用户名
            密码: 密码

            格式二：
            平台名称
            账号: 用户名
            密码: 密码

            格式三：
            平台名称:
            账号：用户名
            密码：密码
        </pre>
        <p class="format-note">注：每组密码信息之间请用空行分隔</p>
        <el-upload
          class="txt-upload"
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :file-list="fileList"
          accept=".txt"
          :limit="1"
        >
          <template #trigger>
            <el-button type="primary">选择文件</el-button>
          </template>
        </el-upload>
        
        <div v-if="importErrors.length > 0" class="import-errors">
          <h4>导入错误</h4>
          <el-alert
            v-for="(error, index) in importErrors"
            :key="index"
            type="warning"
            :title="error"
            :closable="false"
            show-icon
          />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="importPasswords(false)" :loading="importing">导入</el-button>
          <el-tooltip content="导入所有记录，重复的记录会更新已有密码">
            <el-button type="warning" @click="importPasswords(true)" :loading="importing">全部导入</el-button>
          </el-tooltip>
        </span>
      </template>
    </el-dialog>

    <!-- 添加/编辑密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      :title="isEditMode ? (isSharedPassword ? '编辑共享密码' : '编辑密码') : '添加密码'"
      width="500px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="网站名称" prop="domain">
          <el-input 
            v-model="passwordForm.domain" 
            placeholder="给网站起一个便于记忆的名称" 
            :disabled="isSharedPassword" 
          />
        </el-form-item>
        
        <el-form-item label="网站地址" prop="url">
          <el-input 
            v-model="passwordForm.url" 
            placeholder="https://example.com" 
            :disabled="isSharedPassword" 
          />
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="passwordForm.username" 
            placeholder="用户名或邮箱" 
            :disabled="isSharedPassword" 
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="passwordForm.password"
            type="text"
            placeholder="密码"
            :onpaste="() => true"
          >
            <template #append>
              <el-button @click="pasteFromClipboard">粘贴</el-button>
            </template>
          </el-input>
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
        
        <el-form-item>
          <el-button
            type="primary"
            @click="submitPasswordForm"
            :loading="submitting"
          >
            {{ isEditMode ? '保存' : '添加' }}
          </el-button>
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button
            v-if="!isEditMode"
            type="info"
            @click="generatePassword"
          >
            生成密码
          </el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePasswordsStore } from '../../store/passwords'
import BrowserImportDialog from '../../components/BrowserImportDialog.vue'
import {
  Plus as ElIconPlus,
  Refresh as ElIconRefresh,
  Upload as ElIconUpload,
  Download as ElIconDownload,
  Document as ElIconDocument,
  Delete as ElIconDelete
} from '@element-plus/icons-vue'

const route = useRoute()
const passwordsStore = usePasswordsStore()

// 状态
const loading = ref(true)
const syncing = ref(false)
const submitting = ref(false)
const importing = ref(false)
const batchDeleting = ref(false)
const activeTab = ref('my')
const searchQuery = ref('')
const selectedDomain = ref('')
const passwordDialogVisible = ref(false)
const importDialogVisible = ref(false)
const isEditMode = ref(false)
const isSharedPassword = ref(false)
const editingPasswordId = ref(null)
const fileList = ref([])
const importErrors = ref([])
const selectedFile = ref(null)
const browserImportDialogVisible = ref(false)
const selectedPasswords = ref([])

// 密码表单
const passwordForm = ref({
  domain: '',
  url: '',
  username: '',
  password: ''
})

// 表单验证规则
const passwordRules = {
  domain: [
    { required: true, message: '请输入网站名称', trigger: 'blur' }
  ],
  url: [
    { type: 'url', message: '请输入有效的URL', trigger: ['blur', 'change'], validator: (rule, value, callback) => {
      if (value === '' || value === undefined || value === null) {
        callback() // 如果为空，则通过验证
      } else {
        const urlPattern = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w.-]*)*\/?$/
        if (urlPattern.test(value)) {
          callback()
        } else {
          callback(new Error('请输入有效的URL'))
        }
      }
    }}
  ],
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 1, message: '密码不能为空', trigger: 'blur' }
  ]
}

// 表单引用
const passwordFormRef = ref(null)

// 计算属性
const domains = computed(() => {
  return activeTab.value === 'my' ? passwordsStore.domains : passwordsStore.sharedDomains
})

const filteredPasswords = computed(() => {
  let result = [...passwordsStore.passwords]
  
  // 按域名筛选
  if (selectedDomain.value) {
    result = result.filter(p => p.domain === selectedDomain.value)
  }
  
  // 按搜索词筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p => 
      p.domain.toLowerCase().includes(query) || 
      (p.encrypted_username && p.encrypted_username.toLowerCase().includes(query))
    )
  }
  
  // 按更新时间排序
  return result.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
})

const filteredSharedPasswords = computed(() => {
  let result = [...passwordsStore.sharedPasswords]
  
  // 按域名筛选
  if (selectedDomain.value) {
    result = result.filter(p => p.domain === selectedDomain.value)
  }
  
  // 按搜索词筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p => 
      p.domain.toLowerCase().includes(query) || 
      (p.encrypted_username && p.encrypted_username.toLowerCase().includes(query)) ||
      (p.owner_email && p.owner_email.toLowerCase().includes(query))
    )
  }
  
  // 按更新时间排序
  return result.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
})

// 密码强度计算
const passwordStrength = computed(() => {
  const password = passwordForm.value.password
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

// 初始化
onMounted(async () => {
  try {
    // 加载密码数据
    await loadData()
    
    // 检查URL参数
    if (route.query.action === 'add') {
      showAddPasswordDialog()
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
})

// 监听标签页切换，重置筛选条件
watch(activeTab, () => {
  selectedDomain.value = ''
  searchQuery.value = ''
})

// 加载数据
const loadData = async () => {
  // 加载密码
  await passwordsStore.fetchPasswords()
  
  // 加载共享密码
  await passwordsStore.fetchSharedPasswords()
}

// 刷新密码
const refreshPasswords = async () => {
  loading.value = true
  try {
    await loadData()
    ElMessage.success('密码数据已刷新')
  } catch (error) {
    console.error('刷新密码失败:', error)
    ElMessage.error('刷新密码失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 同步密码
const syncPasswords = async () => {
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

// 处理标签页点击
const handleTabClick = () => {
  // 重置筛选条件
  selectedDomain.value = ''
  searchQuery.value = ''
}

// 筛选密码
const filterPasswords = () => {
  // 筛选逻辑在计算属性中实现
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 复制密码
const copyPassword = (password) => {
  try {
    // 检查password对象是否有密码字段，尝试所有可能的密码字段名
    const passwordText = password.encrypted_password || password.password || '';
    
    if (!passwordText) {
      ElMessage.warning(`${password.domain} 的密码为空，无法复制`);
      return;
    }
    
    // 复制到剪贴板
    navigator.clipboard.writeText(passwordText).then(() => {
      ElMessage.success(`已复制 ${password.domain} 的密码`);
    }).catch(err => {
      console.error('无法复制到剪贴板:', err);
      ElMessage.error('复制失败，请检查浏览器权限');
    });
  } catch (error) {
    console.error('复制密码时出错:', error);
    ElMessage.error('复制密码失败');
  }
}

// 显示添加密码对话框
const showAddPasswordDialog = () => {
  isEditMode.value = false
  isSharedPassword.value = false
  editingPasswordId.value = null
  
  // 重置表单
  passwordForm.value = {
    domain: '',
    url: '',
    username: '',
    password: ''
  }
  
  passwordDialogVisible.value = true
}

// 编辑密码
const editPassword = (password) => {
  isEditMode.value = true
  editingPasswordId.value = password.id
  isSharedPassword.value = false
  
  // 填充表单
  passwordForm.value = {
    domain: password.domain,
    url: password.website_url || '',
    username: password.encrypted_username || password.username || '',
    password: password.encrypted_password || password.password || ''
  }
  
  passwordDialogVisible.value = true
}

// 编辑共享密码
const editSharedPassword = (password) => {
  isEditMode.value = true
  isSharedPassword.value = true
  editingPasswordId.value = password.id
  
  // 填充表单，但只允许编辑密码字段
  passwordForm.value = {
    domain: password.domain,
    url: password.website_url || '',
    username: password.encrypted_username || password.username || '',
    password: password.encrypted_password || password.password || ''
  }
  
  passwordDialogVisible.value = true
}

// 确认删除密码
const confirmDeletePassword = (password) => {
  ElMessageBox.confirm(
    `确定要删除 ${password.domain} 的密码吗？`,
    '警告',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    deletePassword(password.id)
  }).catch(() => {})
}

// 删除密码
const deletePassword = async (passwordId) => {
  loading.value = true
  try {
    await passwordsStore.deletePassword(passwordId)
    ElMessage.success('密码已删除')
  } catch (error) {
    console.error('删除密码失败:', error)
    ElMessage.error('删除密码失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理表格选择变化
const handleSelectionChange = (selection) => {
  selectedPasswords.value = selection
}

// 确认批量删除
const confirmBatchDelete = () => {
  if (selectedPasswords.value.length === 0) {
    ElMessage.warning('请先选择要删除的密码')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedPasswords.value.length} 个密码吗？此操作不可撤销。`,
    '批量删除确认',
    {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    batchDeletePasswords()
  }).catch(() => {})
}

// 批量删除密码
const batchDeletePasswords = async () => {
  if (selectedPasswords.value.length === 0) return
  
  batchDeleting.value = true
  try {
    const passwordIds = selectedPasswords.value.map(password => password.id)
    await passwordsStore.batchDeletePasswords(passwordIds)
    
    ElMessage.success(`成功删除 ${selectedPasswords.value.length} 个密码`)
    selectedPasswords.value = []
    
    // 重新加载密码列表
    await passwordsStore.fetchPasswords()
  } catch (error) {
    console.error('批量删除密码失败:', error)
    ElMessage.error('批量删除密码失败，请稍后重试')
  } finally {
    batchDeleting.value = false
  }
}

// 提交密码表单
const submitPasswordForm = async () => {
  if (!passwordFormRef.value) return
  
  try {
    // 表单验证
    await passwordFormRef.value.validate()
    
    // 设置提交状态
    submitting.value = true
    
    // 直接使用用户输入的domain作为网站名称
    const domain = passwordForm.value.domain
    
    // 准备密码数据
    const passwordData = {
      domain,
      url: passwordForm.value.url || '',
      username: passwordForm.value.username,
      password: passwordForm.value.password
    }
    
    if (isEditMode.value) {
      if (isSharedPassword.value) {
        // 更新共享密码，只更新密码字段
        await passwordsStore.updateSharedPassword(editingPasswordId.value, {
          password: passwordForm.value.password
        })
        ElMessage.success('共享密码已更新')
        // 刷新共享密码列表
        await passwordsStore.fetchSharedPasswords()
      } else {
        // 更新自己的密码
        await passwordsStore.updatePassword(editingPasswordId.value, passwordData)
        ElMessage.success('密码已更新')
        // 刷新密码列表
        await passwordsStore.fetchPasswords()
      }
    } else {
      // 添加密码
      await passwordsStore.addPassword(passwordData)
      ElMessage.success('密码已添加')
    }
    
    // 关闭对话框
    passwordDialogVisible.value = false
  } catch (error) {
    console.error('提交密码失败:', error)
    ElMessage.error('提交密码失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// 生成随机密码
const generatePassword = () => {
  const length = 16
  const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+'
  let password = ''
  
  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * charset.length)
    password += charset[randomIndex]
  }
  
  passwordForm.value.password = password
}

// 从剪贴板粘贴密码
const pasteFromClipboard = async () => {
  try {
    const text = await navigator.clipboard.readText();
    passwordForm.value.password = text;
    ElMessage.success('密码已从剪贴板粘贴');
  } catch (err) {
    console.error('无法访问剪贴板:', err);
    ElMessage.error('无法访问剪贴板，请检查浏览器权限设置');
  }
}

// 显示导入对话框
const showImportDialog = () => {
  importDialogVisible.value = true
  fileList.value = []
  importErrors.value = []
  selectedFile.value = null
}

// 处理文件选择
const handleFileChange = (file) => {
  selectedFile.value = file.raw
  fileList.value = [file]
}

// 解析TXT文件内容
const parseTxtContent = (content) => {
  // 分割内容为不同的密码项（允许多种分隔方式）
  const items = content.split(/\n\s*\n/)
  const passwords = []
  const errors = []
  
  items.forEach((item, index) => {
    try {
      // 去除首尾空白
      const trimmedItem = item.trim()
      if (!trimmedItem) return
      
      // 分析每一项
      const lines = trimmedItem.split('\n')
      
      // 至少需要包含平台名称、账号和密码信息
      if (lines.length < 2) {
        errors.push(`第${index + 1}条记录格式不正确: 信息不完整`)
        return
      }
      
      // 提取平台名称（通常是第一行）
      const domainLine = lines[0].trim()
      // 移除可能的冒号
      const domain = domainLine.endsWith(':') ? domainLine.slice(0, -1).trim() : domainLine.replace(':', '').trim()
      
      // 提取账户信息（查找包含"账户:"或"账号:"的行）
      const usernameKeywords = ['账户:', '账号:', '账户：', '账号：', '用户名:', '用户名：']
      const usernameLine = lines.find(line => 
        usernameKeywords.some(keyword => line.includes(keyword))
      )
      
      if (!usernameLine) {
        errors.push(`第${index + 1}条记录格式不正确: 缺少账户信息`)
        return
      }
      
      // 提取用户名（考虑多种分隔符）
      let username = ''
      for (const keyword of usernameKeywords) {
        if (usernameLine.includes(keyword)) {
          username = usernameLine.split(keyword)[1]?.trim()
          break
        }
      }
      
      // 提取密码信息（查找包含"密码:"的行）
      const passwordKeywords = ['密码:', '密码：']
      const passwordLine = lines.find(line => 
        passwordKeywords.some(keyword => line.includes(keyword))
      )
      
      if (!passwordLine) {
        errors.push(`第${index + 1}条记录格式不正确: 缺少密码信息`)
        return
      }
      
      // 提取密码（考虑多种分隔符）
      let password = ''
      for (const keyword of passwordKeywords) {
        if (passwordLine.includes(keyword)) {
          password = passwordLine.split(keyword)[1]?.trim()
          break
        }
      }
      
      // 验证必要字段
      if (!domain) {
        errors.push(`第${index + 1}条记录格式不正确: 缺少平台名称`)
        return
      }
      if (!username) {
        errors.push(`第${index + 1}条记录格式不正确: 账户名称为空`)
        return
      }
      if (!password) {
        errors.push(`第${index + 1}条记录格式不正确: 密码为空`)
        return
      }
      
      // 添加到密码列表
      passwords.push({
        domain,
        url: domain.includes('.') ? `https://${domain}` : '',
        username,
        password
      })
    } catch (error) {
      errors.push(`第${index + 1}条记录解析失败: ${error.message}`)
    }
  })
  
  return { passwords, errors }
}
// 显示浏览器导入对话框
const showBrowserImportDialog = () => {
  browserImportDialogVisible.value = true
}

// 导入成功处理
const onImportSuccess = async (count) => {
  // 重新加载密码列表
  await passwordsStore.fetchPasswords()
}

// 导入密码
const importPasswords = async (forceImport = false) => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的TXT文件')
    return
  }
  
  importing.value = true
  importErrors.value = []
  
  // 确认全部导入
  if (forceImport) {
    try {
      await ElMessageBox.confirm(
        '全部导入将会导入所有记录，如果存在重复的账号密码记录，将会覆盖已有的记录。是否继续？',
        '确认操作',
        {
          confirmButtonText: '确认导入',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
    } catch (e) {
      importing.value = false
      return // 用户取消操作
    }
  }
  
  try {
    // 读取文件内容
    const content = await readFileAsText(selectedFile.value)
    
    // 解析文件内容
    const { passwords, errors } = parseTxtContent(content)
    importErrors.value = errors
    
    if (passwords.length === 0) {
      ElMessage.warning('没有找到有效的密码记录')
      return
    }
    
    // 发送到后端导入
    const response = await passwordsStore.importPasswords(passwords, forceImport)
    
    // 显示导入结果
    if (response.importedCount > 0) {
      ElMessage.success(`成功导入 ${response.importedCount} 条密码记录`)
      
      if (response.skippedCount > 0) {
        // 显示跳过的详情
        const skippedDetails = response.skippedDetails || []
        importErrors.value = [...importErrors.value, ...skippedDetails.map(detail => `跳过: ${detail}`)]
        ElMessage.warning(`${response.skippedCount} 条记录被跳过，请查看详细信息`)
      } else {
        // 导入成功且没有跳过记录，关闭对话框
        importDialogVisible.value = false
      }
      
      // 重新加载密码列表
      await passwordsStore.fetchPasswords()
    } else {
      if (response.errors && response.errors.length > 0) {
        // 显示错误详情
        importErrors.value = [...importErrors.value, ...response.errors]
      }
      ElMessage.warning('没有成功导入任何密码记录，请检查文件格式')
    }
  } catch (error) {
    console.error('导入密码失败:', error)
    ElMessage.error('导入密码失败: ' + (error.message || '未知错误'))
  } finally {
    importing.value = false
  }
}

// 辅助函数：读取文件内容为文本
const readFileAsText = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = (e) => reject(new Error('读取文件失败'))
    reader.readAsText(file)
  })
}
</script>

<style scoped>
.passwords-view {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

/* 筛选区域样式优化 */
.filter-section {
  margin-bottom: 24px;
}

.filter-card {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
  transition: all 0.3s ease;
}

.filter-card:hover {
  border-color: #409eff;
  box-shadow: 0 8px 25px rgba(64, 158, 255, 0.15);
}

.filter-header {
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f2f5;
}

.filter-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.filter-icon {
  margin-right: 8px;
  color: #409eff;
  font-size: 18px;
}

.filter-content {
  align-items: flex-end;
}

.filter-item {
  margin-bottom: 0;
}

.filter-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
  line-height: 1.4;
}

.search-input {
  border-radius: 8px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.search-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.domain-select :deep(.el-select__wrapper) {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.domain-select :deep(.el-select__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.action-btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.batch-delete-btn {
  position: relative;
  overflow: hidden;
}

.batch-delete-btn:not(:disabled):hover {
  background: linear-gradient(135deg, #f56c6c 0%, #e53e3e 100%);
}

.batch-delete-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.password-list-card {
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

.import-dialog-content {
  margin-bottom: 20px;
}

.import-dialog-content pre {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 10px;
  font-family: monospace;
  overflow-x: auto;
}

.txt-upload {
  margin-top: 20px;
}

.import-errors {
  margin-top: 20px;
  max-height: 200px;
  overflow-y: auto;
}

.import-errors h4 {
  margin-bottom: 10px;
  color: #e6a23c;
}

.import-errors .el-alert {
  margin-bottom: 8px;
}

.format-note {
  color: #909399;
  font-size: 12px;
  margin-top: 5px;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .action-buttons {
    justify-content: flex-start;
  }
  
  .action-btn {
    font-size: 13px;
    padding: 8px 12px;
  }
}

@media (max-width: 768px) {
  .filter-content .el-col {
    margin-bottom: 16px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
