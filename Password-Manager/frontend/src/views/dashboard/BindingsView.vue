<template>
  <div class="bindings-view">
    <div class="page-header">
      <h1 class="page-title">账号绑定</h1>
      <el-button type="primary" @click="showBindAccountDialog">
        <el-icon><el-icon-plus /></el-icon>
        绑定新账号
      </el-button>
    </div>
    
    <!-- 绑定账号列表 -->
    <el-card v-loading="loading" class="binding-card">
      <template #header>
        <div class="card-header">
          <span>已绑定账号</span>
          <el-button type="text" @click="refreshBindings" :disabled="loading">
            <el-icon><el-icon-refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-table
        :data="bindings"
        style="width: 100%"
        v-if="bindings.length > 0"
      >
        <el-table-column prop="bound_account_email" label="账号" />
        <el-table-column label="绑定状态" width="120">
          <template #default="scope">
            <el-tag type="success">已绑定</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="权限" width="120">
          <template #default="scope">
            <el-select
              v-model="scope.row.permissions"
              size="small"
              style="width: 90px"
              @change="updatePermissions(scope.row)"
            >
              <el-option label="只读" value="read" />
              <el-option label="读写" value="write" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="绑定时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="scope">
            <el-button
              size="small"
              type="danger"
              plain
              @click="confirmUnbindAccount(scope.row)"
            >
              解除绑定
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无绑定账号" />
    </el-card>
    
    <!-- 绑定请求列表 -->
    <el-card v-loading="loading" class="binding-card">
      <template #header>
        <div class="card-header">
          <span>待处理的绑定请求</span>
          <el-badge :value="pendingRequests.length" :hidden="pendingRequests.length === 0" class="request-badge">
            <el-button type="text" @click="refreshBindings" :disabled="loading">
              <el-icon><el-icon-refresh /></el-icon>
              刷新
            </el-button>
          </el-badge>
        </div>
      </template>
      
      <el-table
        :data="pendingRequests"
        style="width: 100%"
        v-if="pendingRequests.length > 0"
      >
        <el-table-column prop="requester_email" label="请求账号" />
        <el-table-column label="请求时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="scope">
            <el-button
              size="small"
              type="success"
              plain
              @click="acceptBindingRequest(scope.row)"
              :loading="processingRequest === scope.row.id"
            >
              接受
            </el-button>
            <el-button
              size="small"
              type="danger"
              plain
              @click="rejectBindingRequest(scope.row)"
              :loading="processingRequest === scope.row.id"
            >
              拒绝
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-else description="暂无待处理的绑定请求" />
    </el-card>
    
    <!-- 绑定账号对话框 -->
    <el-dialog
      v-model="bindAccountDialogVisible"
      title="绑定新账号"
      width="500px"
    >
      <el-form
        ref="bindAccountFormRef"
        :model="bindAccountForm"
        :rules="bindAccountRules"
        label-width="100px"
      >
        <el-form-item label="目标邮箱" prop="targetEmail">
          <el-input
            v-model="bindAccountForm.targetEmail"
            placeholder="请输入要绑定的账号邮箱"
            type="email"
          />
        </el-form-item>
        
        <div class="binding-info">
          <el-alert
            title="绑定说明"
            type="info"
            :closable="false"
          >
            <p>绑定后，对方可以访问您的密码库。</p>
            <p>对方需要接受您的绑定请求才能完成绑定。</p>
          </el-alert>
        </div>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="submitBindAccountForm"
            :loading="submitting"
          >
            发送绑定请求
          </el-button>
          <el-button @click="bindAccountDialogVisible = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBindingsStore } from '../../store/bindings'
import {
  Plus as ElIconPlus,
  Refresh as ElIconRefresh
} from '@element-plus/icons-vue'

const bindingsStore = useBindingsStore()

// 状态
const loading = ref(true)
const submitting = ref(false)
const processingRequest = ref(null)
const bindAccountDialogVisible = ref(false)

// 绑定账号表单
const bindAccountForm = ref({
  targetEmail: ''
})

// 表单验证规则
const bindAccountRules = {
  targetEmail: [
    { required: true, message: '请输入目标邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' }
  ]
}

// 表单引用
const bindAccountFormRef = ref(null)

// 绑定关系和请求
const bindings = ref([])
const pendingRequests = ref([])

// 初始化
onMounted(async () => {
  try {
    // 加载绑定数据
    await loadBindingsData()
  } catch (error) {
    console.error('加载绑定数据失败:', error)
    ElMessage.error('加载绑定数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
})

// 加载绑定数据
const loadBindingsData = async () => {
  const data = await bindingsStore.fetchBindings()
  bindings.value = data.bindings
  pendingRequests.value = data.pendingRequests
}

// 刷新绑定数据
const refreshBindings = async () => {
  loading.value = true
  try {
    await loadBindingsData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    console.error('刷新绑定数据失败:', error)
    ElMessage.error('刷新绑定数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString()
}

// 显示绑定账号对话框
const showBindAccountDialog = () => {
  // 重置表单
  bindAccountForm.value = {
    targetEmail: ''
  }
  
  bindAccountDialogVisible.value = true
}

// 提交绑定账号表单
const submitBindAccountForm = async () => {
  if (!bindAccountFormRef.value) return
  
  try {
    // 表单验证
    await bindAccountFormRef.value.validate()
    
    // 设置提交状态
    submitting.value = true
    
    // 发送绑定请求
    await bindingsStore.bindAccount(bindAccountForm.value.targetEmail)
    
    // 关闭对话框
    bindAccountDialogVisible.value = false
    
    // 显示成功消息
    ElMessage.success('绑定请求已发送')
  } catch (error) {
    console.error('发送绑定请求失败:', error)
    ElMessage.error(error.response?.data?.message || '发送绑定请求失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

// 更新绑定权限
const updatePermissions = async (binding) => {
  try {
    await bindingsStore.updateBindingPermissions(binding.id, binding.permissions)
    ElMessage.success('权限已更新')
  } catch (error) {
    console.error('更新权限失败:', error)
    ElMessage.error('更新权限失败，请稍后重试')
    
    // 恢复原始权限
    await refreshBindings()
  }
}

// 确认解除绑定
const confirmUnbindAccount = (binding) => {
  ElMessageBox.confirm(
    `确定要解除与 ${binding.bound_account_email} 的绑定吗？`,
    '警告',
    {
      confirmButtonText: '解除绑定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    unbindAccount(binding)
  }).catch(() => {})
}

// 解除绑定
const unbindAccount = async (binding) => {
  loading.value = true
  try {
    await bindingsStore.unbindAccount(binding.id)
    ElMessage.success('已解除绑定')
    await loadBindingsData()
  } catch (error) {
    console.error('解除绑定失败:', error)
    ElMessage.error('解除绑定失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 接受绑定请求
const acceptBindingRequest = async (request) => {
  processingRequest.value = request.id
  try {
    await bindingsStore.acceptBindingRequest(request.id)
    ElMessage.success('已接受绑定请求')
    await loadBindingsData()
  } catch (error) {
    console.error('接受绑定请求失败:', error)
    ElMessage.error('接受绑定请求失败，请稍后重试')
  } finally {
    processingRequest.value = null
  }
}

// 拒绝绑定请求
const rejectBindingRequest = async (request) => {
  processingRequest.value = request.id
  try {
    await bindingsStore.rejectBindingRequest(request.id)
    ElMessage.success('已拒绝绑定请求')
    await loadBindingsData()
  } catch (error) {
    console.error('拒绝绑定请求失败:', error)
    ElMessage.error('拒绝绑定请求失败，请稍后重试')
  } finally {
    processingRequest.value = null
  }
}
</script>

<style scoped>
.bindings-view {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.binding-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.request-badge {
  margin-right: 10px;
}

.binding-info {
  margin-bottom: 20px;
}

.binding-info p {
  margin: 5px 0;
}
</style>
