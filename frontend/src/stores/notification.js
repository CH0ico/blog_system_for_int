import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'

export const useNotificationStore = defineStore('notification', () => {
  const toast = useToast()
  
  // 状态
  const notifications = ref([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const hasNewNotification = ref(false)
  
  // 计算属性
  const hasNotifications = computed(() => (notifications.value || []).length > 0)
  const unreadNotifications = computed(() => 
    (notifications.value || []).filter(n => !n.is_read)
  )
  
  // 获取通知列表
  const fetchNotifications = async (params = {}) => {
    loading.value = true
    try {
      const response = await api.get('/notifications', { params })
      const { notifications: notificationsData, unread_count } = response.data
      
      if (params.page && params.page > 1) {
        // 如果是加载更多，追加到现有列表
        notifications.value.push(...notificationsData)
      } else {
        // 否则替换现有列表
        notifications.value = notificationsData
      }
      
      unreadCount.value = unread_count
      hasNewNotification.value = unread_count > 0
      
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || '获取通知失败'
      toast.error(message)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 添加通知（通过Socket接收）
  const addNotification = (notification) => {
    // 添加到列表开头
    notifications.value.unshift(notification)
    
    // 更新未读计数
    if (!notification.is_read) {
      unreadCount.value += 1
      hasNewNotification.value = true
    }
    
    // 触发新通知事件
    window.dispatchEvent(new CustomEvent('notification:new', { detail: notification }))
  }
  
  // 标记通知为已读
  const markAsRead = async (notificationId) => {
    try {
      await api.put(`/notifications/${notificationId}/read`)
      
      // 更新本地状态
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification && !notification.is_read) {
        notification.is_read = true
        unreadCount.value = Math.max(0, unreadCount.value - 1)
        
        if (unreadCount.value === 0) {
          hasNewNotification.value = false
        }
      }
    } catch (error) {
      const message = error.response?.data?.message || '标记已读失败'
      toast.error(message)
      throw error
    }
  }
  
  // 标记所有通知为已读
  const markAllAsRead = async () => {
    try {
      // 批量标记已读
      const unreadIds = unreadNotifications.value.map(n => n.id)
      
      await Promise.all(
        unreadIds.map(id => markAsRead(id))
      )
      
      toast.success('已标记所有通知为已读')
    } catch (error) {
      const message = error.response?.data?.message || '标记失败'
      toast.error(message)
      throw error
    }
  }
  
  // 标记通知为已读（本地操作，不发送请求）
  const markNotificationsAsRead = () => {
    notifications.value.forEach(notification => {
      notification.is_read = true
    })
    unreadCount.value = 0
    hasNewNotification.value = false
  }
  
  // 删除通知
  const deleteNotification = async (notificationId) => {
    try {
      await api.delete(`/notifications/${notificationId}`)
      
      // 从列表中移除
      const index = notifications.value.findIndex(n => n.id === notificationId)
      if (index !== -1) {
        const notification = notifications.value[index]
        
        // 更新未读计数
        if (!notification.is_read) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
          if (unreadCount.value === 0) {
            hasNewNotification.value = false
          }
        }
        
        notifications.value.splice(index, 1)
      }
      
      toast.success('通知已删除')
    } catch (error) {
      const message = error.response?.data?.message || '删除失败'
      toast.error(message)
      throw error
    }
  }
  
  // 清空通知列表
  const clearNotifications = () => {
    notifications.value = []
    unreadCount.value = 0
    hasNewNotification.value = false
  }
  
  // 格式化通知时间
  const formatNotificationTime = (timestamp) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diff = now - time
    
    if (diff < 60000) { // 1分钟内
      return '刚刚'
    } else if (diff < 3600000) { // 1小时内
      return `${Math.floor(diff / 60000)}分钟前`
    } else if (diff < 86400000) { // 1天内
      return `${Math.floor(diff / 3600000)}小时前`
    } else if (diff < 2592000000) { // 30天内
      return `${Math.floor(diff / 86400000)}天前`
    } else {
      return time.toLocaleDateString()
    }
  }
  
  // 获取通知图标
  const getNotificationIcon = (type) => {
    const iconMap = {
      'like': 'Heart',
      'comment': 'ChatDotRound',
      'comment_reply': 'ChatLineRound',
      'follow': 'User',
      'new_post': 'Document',
      'system': 'Bell'
    }
    
    return iconMap[type] || 'Bell'
  }
  
  // 获取通知类型描述
  const getNotificationTypeText = (type) => {
    const typeMap = {
      'like': '点赞',
      'comment': '评论',
      'comment_reply': '回复',
      'follow': '关注',
      'new_post': '新文章',
      'system': '系统'
    }
    
    return typeMap[type] || '通知'
  }
  
  // 初始化
  const initialize = () => {
    // 定时清理过期通知（可选）
    setInterval(() => {
      // 清理30天前的通知
      const thirtyDaysAgo = new Date()
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
      
      notifications.value = notifications.value.filter(notification => {
        return new Date(notification.created_at) > thirtyDaysAgo
      })
    }, 86400000) // 每天执行一次
  }
  
  return {
    notifications,
    unreadCount,
    loading,
    hasNewNotification,
    hasNotifications,
    unreadNotifications,
    fetchNotifications,
    addNotification,
    markAsRead,
    markAllAsRead,
    markNotificationsAsRead,
    deleteNotification,
    clearNotifications,
    formatNotificationTime,
    getNotificationIcon,
    getNotificationTypeText,
    initialize
  }
})