<template>
  <el-dialog
    v-model="dialogVisible"
    title="从浏览器导入密码"
    width="560px"
  >
    <div class="browser-import-dialog-content">
      <p>请从浏览器导出密码文件后上传：</p>
      
      <div class="browser-instructions">
        <h4>Chrome 浏览器</h4>
        <ol>
          <li>打开 <code>chrome://password-manager/passwords</code></li>
          <li>点击右上角的"⋮"图标</li>
          <li>选择"导出密码"</li>
          <li>保存CSV文件</li>
        </ol>
        
        <h4>Edge 浏览器</h4>
        <ol>
          <li>打开 <code>edge://wallet/passwords</code></li>
          <li>点击"⋯"菜单</li> 
          <li>选择"导出密码"</li>
          <li>保存CSV文件</li>
        </ol>
      </div>
      
      <el-upload
        class="csv-upload"
        action="#"
        :auto-upload="false"
        :on-change="handleFileChange"
        :file-list="fileList"
        accept=".csv"
        :limit="1"
      >
        <template #trigger>
          <el-button type="primary">选择CSV文件</el-button>
        </template>
        <template #tip>
          <div class="el-upload__tip">
            仅支持Chrome和Edge浏览器导出的CSV格式密码文件
          </div>
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
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="importCSVPasswords(false)" :loading="importing">导入</el-button>
        <el-tooltip content="导入所有记录，重复的记录会更新已有密码">
          <el-button type="warning" @click="importCSVPasswords(true)" :loading="importing">全部导入</el-button>
        </el-tooltip>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, defineEmits, defineProps, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { usePasswordsStore } from '../store/passwords'

const passwordsStore = usePasswordsStore()
const emit = defineEmits(['update:visible', 'imported'])

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

// 状态
const dialogVisible = ref(props.visible)
const importing = ref(false)
const fileList = ref([])
const importErrors = ref([])
const selectedFile = ref(null)

// 监听visible变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
})

// 监听dialog可见性变化
watch(() => dialogVisible.value, (newVal) => {
  emit('update:visible', newVal)
  if (!newVal) {
    // 关闭对话框时重置状态
    fileList.value = []
    importErrors.value = []
    selectedFile.value = null
  }
})

// 处理文件选择
const handleFileChange = (file) => {
  selectedFile.value = file.raw
  fileList.value = [file]
}

// 关闭对话框
const closeDialog = () => {
  dialogVisible.value = false
}

// 读取文件内容
const readFileAsText = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.onerror = (e) => reject(new Error('读取文件失败'))
    reader.readAsText(file)
  })
}

// 解析CSV文件
const parseCSVContent = (content) => {
  const passwords = []
  const errors = []
  
  try {
    // 分割行
    const lines = content.split('\n')
    if (lines.length < 2) {
      throw new Error('CSV文件格式不正确或为空')
    }
    
    // 解析标题行
    const headers = lines[0].trim().split(',')
    
    // 检查必要的列
    const nameIndex = headers.findIndex(h => h.toLowerCase() === 'name')
    const urlIndex = headers.findIndex(h => h.toLowerCase() === 'url')
    const usernameIndex = headers.findIndex(h => h.toLowerCase() === 'username')
    const passwordIndex = headers.findIndex(h => h.toLowerCase() === 'password')
    
    if (nameIndex === -1 || urlIndex === -1 || usernameIndex === -1 || passwordIndex === -1) {
      throw new Error('CSV文件缺少必要的列(name/url/username/password)')
    }
    
    // 处理数据行
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue // 跳过空行
      
      // 正确处理CSV中的引号和逗号
      const fields = []
      let field = ''
      let inQuotes = false
      
      for (let j = 0; j < line.length; j++) {
        const char = line[j]
        
        if (char === '"') {
          // 处理引号
          if (inQuotes && j+1 < line.length && line[j+1] === '"') {
            // 两个连续引号在引号内表示一个引号字符
            field += '"'
            j++ // 跳过下一个引号
          } else {
            // 切换引号状态
            inQuotes = !inQuotes
          }
        } else if (char === ',' && !inQuotes) {
          // 逗号分隔符（不在引号内）
          fields.push(field)
          field = ''
        } else {
          // 常规字符
          field += char
        }
      }
      
      // 添加最后一个字段
      fields.push(field)
      
      // 验证字段数量
      if (fields.length <= Math.max(nameIndex, urlIndex, usernameIndex, passwordIndex)) {
        errors.push(`第${i}行: 字段数不足`)
        continue
      }
      
      const domain = fields[nameIndex]
      const url = fields[urlIndex]
      const username = fields[usernameIndex]
      const password = fields[passwordIndex]
      
      // 验证必要字段
      if (!domain) {
        errors.push(`第${i}行: 缺少网站名称`)
        continue
      }
      
      if (!username) {
        errors.push(`第${i}行: 缺少用户名`)
        continue
      }
      
      if (!password) {
        errors.push(`第${i}行: 缺少密码`)
        continue
      }
      
      // 添加到密码列表
      passwords.push({
        domain,
        url,
        username,
        password
      })
    }
  } catch (error) {
    errors.push(`解析CSV文件失败: ${error.message}`)
  }
  
  return { passwords, errors }
}

// 导入CSV密码
const importCSVPasswords = async (forceImport = false) => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择要导入的CSV文件')
    return
  }
  
  // 检查文件类型
  if (!selectedFile.value.name.toLowerCase().endsWith('.csv')) {
    ElMessage.warning('请上传CSV格式的文件')
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
    const { passwords, errors } = parseCSVContent(content)
    importErrors.value = errors
    
    if (passwords.length === 0) {
      ElMessage.warning('没有找到有效的密码记录')
      importing.value = false
      return
    }
    
    // 使用TXT导入的API导入密码（避免CORS问题）
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
        closeDialog()
      }
      
      // 通知父组件导入成功
      emit('imported', response.importedCount)
    } else {
      if (response.errors && response.errors.length > 0) {
        // 显示错误详情
        importErrors.value = [...importErrors.value, ...response.errors]
      }
      ElMessage.warning('没有成功导入任何密码记录，请检查文件格式是否正确')
    }
  } catch (error) {
    console.error('导入密码失败:', error)
    ElMessage.error('导入密码失败: ' + (error.message || '未知错误'))
    importErrors.value.push('导入过程中发生错误: ' + (error.message || '未知错误'))
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.browser-import-dialog-content {
  margin-bottom: 20px;
}

.browser-instructions {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  margin: 10px 0 20px;
}

.browser-instructions h4 {
  margin-bottom: 8px;
  font-weight: 500;
  color: #409EFF;
}

.browser-instructions ol {
  padding-left: 20px;
  margin-bottom: 15px;
}

.browser-instructions li {
  margin-bottom: 5px;
}

.browser-instructions code {
  background-color: #e9f3ff;
  padding: 2px 5px;
  border-radius: 3px;
  font-family: monospace;
}

.csv-upload {
  margin-top: 15px;
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

.el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>