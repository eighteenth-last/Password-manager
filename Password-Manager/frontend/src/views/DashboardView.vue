<template>
  <div class="dashboard-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo-container">
        <div class="logo">🔒</div>
        <h1>密码管家</h1>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        background-color="#001529"
        text-color="#fff"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><el-icon-menu /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/passwords">
          <el-icon><el-icon-key /></el-icon>
          <span>密码管理</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/bindings">
          <el-icon><el-icon-connection /></el-icon>
          <span>账号绑定</span>
        </el-menu-item>
        
        <el-menu-item index="/dashboard/settings">
          <el-icon><el-icon-setting /></el-icon>
          <span>设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主要内容区域 -->
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-button
            type="text"
            @click="toggleSidebar"
            class="toggle-sidebar-btn"
          >
            <el-icon><el-icon-fold /></el-icon>
          </el-button>
          
          <div class="breadcrumb">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="currentRoute.name !== 'dashboard-home'">
                {{ getMenuTitle(currentRoute.name) }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>
        </div>
        
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <span class="user-dropdown-link">
              {{ userEmail }}
              <el-icon class="el-icon--right"><el-icon-arrow-down /></el-icon>
            </span>
            
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="settings">
                  <el-icon><el-icon-setting /></el-icon>
                  设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><el-icon-switch-button /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区域 -->
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '../store/auth'
import {
  Menu as ElIconMenu,
  Key as ElIconKey,
  Connection as ElIconConnection,
  Setting as ElIconSetting,
  Fold as ElIconFold,
  ArrowDown as ElIconArrowDown,
  SwitchButton as ElIconSwitchButton
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 侧边栏折叠状态
const sidebarCollapsed = ref(false)

// 当前路由
const currentRoute = computed(() => route)

// 当前活动菜单
const activeMenu = computed(() => route.path)

// 用户邮箱
const userEmail = computed(() => authStore.userEmail)

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 获取菜单标题
const getMenuTitle = (routeName) => {
  const menuTitles = {
    'dashboard-home': '首页',
    'passwords': '密码管理',
    'bindings': '账号绑定',
    'settings': '设置'
  }
  return menuTitles[routeName] || '未知页面'
}

// 处理下拉菜单命令
const handleCommand = (command) => {
  if (command === 'settings') {
    router.push('/dashboard/settings')
  } else if (command === 'logout') {
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
}
</script>

<style scoped>
.dashboard-container {
  height: 100vh;
  display: flex;
}

.sidebar {
  background-color: #001529;
  color: #fff;
  height: 100vh;
  overflow-y: auto;
  transition: width 0.3s;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #002140;
}

.logo {
  font-size: 24px;
  margin-right: 10px;
}

.logo-container h1 {
  font-size: 18px;
  font-weight: 500;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
}

.sidebar-menu {
  border-right: none;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
}

.toggle-sidebar-btn {
  margin-right: 15px;
}

.breadcrumb {
  font-size: 14px;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #606266;
  font-size: 14px;
}

.user-dropdown-link:hover {
  color: #409EFF;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #f5f7fa;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
