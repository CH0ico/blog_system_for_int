import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

// 设置中文语言
dayjs.locale('zh-cn')

/**
 * 格式化时间
 * @param {string|Date} time - 时间字符串或Date对象
 * @param {string} format - 格式字符串，默认为'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的时间字符串
 */
export function formatTime(time, format = 'YYYY-MM-DD HH:mm:ss') {
  if (!time) return ''
  return dayjs(time).format(format)
}

/**
 * 相对时间格式化
 * @param {string|Date} time - 时间字符串或Date对象
 * @returns {string} 相对时间描述
 */
export function formatRelativeTime(time) {
  if (!time) return ''
  return dayjs(time).fromNow()
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期字符串或Date对象
 * @param {string} format - 格式字符串，默认为'YYYY-MM-DD'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return ''
  return dayjs(date).format(format)
}

/**
 * 截断文本
 * @param {string} text - 原始文本
 * @param {number} maxLength - 最大长度
 * @param {string} suffix - 后缀字符串，默认为'...'
 * @returns {string} 截断后的文本
 */
export function truncateText(text, maxLength = 100, suffix = '...') {
  if (!text || typeof text !== 'string') return ''
  
  if (text.length <= maxLength) {
    return text
  }
  
  return text.slice(0, maxLength - suffix.length) + suffix
}

/**
 * 生成文章摘要
 * @param {string} content - 文章内容（HTML格式）
 * @param {number} maxLength - 最大长度，默认为200
 * @returns {string} 纯文本摘要
 */
export function generateExcerpt(content, maxLength = 200) {
  if (!content) return ''
  
  // 移除HTML标签
  const text = content.replace(/<[^>]*>/g, '')
  
  // 移除多余的空白字符
  const cleanText = text.replace(/\s+/g, ' ').trim()
  
  return truncateText(cleanText, maxLength)
}

/**
 * 格式化数字
 * @param {number} num - 数字
 * @returns {string} 格式化后的数字字符串
 */
export function formatNumber(num) {
  if (!num || typeof num !== 'number') return '0'
  
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  
  return num.toString()
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @returns {string} 格式化后的文件大小字符串
 */
export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 格式化访问量
 * @param {number} views - 访问量
 * @returns {string} 格式化后的访问量字符串
 */
export function formatViews(views) {
  return formatNumber(views)
}

/**
 * 格式化点赞数
 * @param {number} likes - 点赞数
 * @returns {string} 格式化后的点赞数字符串
 */
export function formatLikes(likes) {
  return formatNumber(likes)
}

/**
 * 格式化评论数
 * @param {number} comments - 评论数
 * @returns {string} 格式化后的评论数字符串
 */
export function formatComments(comments) {
  return formatNumber(comments)
}

/**
 * 格式化收藏数
 * @param {number} favorites - 收藏数
 * @returns {string} 格式化后的收藏数字符串
 */
export function formatFavorites(favorites) {
  return formatNumber(favorites)
}

/**
 * 格式化用户数
 * @param {number} users - 用户数
 * @returns {string} 格式化后的用户数字符串
 */
export function formatUsers(users) {
  return formatNumber(users)
}

/**
 * 格式化在线时间
 * @param {number} seconds - 秒数
 * @returns {string} 格式化后的在线时间字符串
 */
export function formatOnlineTime(seconds) {
  if (!seconds || seconds < 0) return '0秒'
  
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  
  if (days > 0) {
    return `${days}天${hours}小时`
  } else if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else if (minutes > 0) {
    return `${minutes}分钟${secs}秒`
  } else {
    return `${secs}秒`
  }
}

/**
 * 格式化持续时间
 * @param {number} milliseconds - 毫秒数
 * @returns {string} 格式化后的持续时间字符串
 */
export function formatDuration(milliseconds) {
  if (!milliseconds || milliseconds < 0) return '0ms'
  
  const seconds = Math.floor(milliseconds / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  
  if (hours > 0) {
    return `${hours}h ${minutes % 60}m ${seconds % 60}s`
  } else if (minutes > 0) {
    return `${minutes}m ${seconds % 60}s`
  } else {
    return `${seconds}s`
  }
}

/**
 * 格式化百分比
 * @param {number} value - 数值
 * @param {number} total - 总数
 * @param {number} decimals - 小数位数，默认为1
 * @returns {string} 格式化后的百分比字符串
 */
export function formatPercentage(value, total, decimals = 1) {
  if (!total || total === 0) return '0%'
  
  const percentage = (value / total) * 100
  return `${percentage.toFixed(decimals)}%`
}

/**
 * 格式化货币
 * @param {number} amount - 金额
 * @param {string} currency - 货币代码，默认为'CNY'
 * @returns {string} 格式化后的货币字符串
 */
export function formatCurrency(amount, currency = 'CNY') {
  if (!amount || typeof amount !== 'number') return '¥0.00'
  
  try {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: currency
    }).format(amount)
  } catch (error) {
    return `¥${amount.toFixed(2)}`
  }
}

/**
 * 格式化URL
 * @param {string} url - URL字符串
 * @returns {string} 格式化后的URL字符串
 */
export function formatUrl(url) {
  if (!url) return ''
  
  // 移除协议部分
  return url.replace(/^https?:\/\//, '')
}

/**
 * 格式化邮箱
 * @param {string} email - 邮箱地址
 * @returns {string} 格式化后的邮箱字符串
 */
export function formatEmail(email) {
  if (!email) return ''
  
  // 如果邮箱太长，进行截断
  if (email.length > 25) {
    const [username, domain] = email.split('@')
    if (username && domain) {
      const truncatedUsername = username.length > 10 ? username.slice(0, 10) + '...' : username
      return `${truncatedUsername}@${domain}`
    }
  }
  
  return email
}

/**
 * 格式化用户名
 * @param {string} username - 用户名
 * @param {number} maxLength - 最大长度，默认为15
 * @returns {string} 格式化后的用户名
 */
export function formatUsername(username, maxLength = 15) {
  if (!username) return ''
  
  return truncateText(username, maxLength)
}

/**
 * 格式化昵称
 * @param {string} nickname - 昵称
 * @param {number} maxLength - 最大长度，默认为20
 * @returns {string} 格式化后的昵称
 */
export function formatNickname(nickname, maxLength = 20) {
  if (!nickname) return ''
  
  return truncateText(nickname, maxLength)
}

/**
 * 格式化标签名称
 * @param {string} tagName - 标签名称
 * @param {number} maxLength - 最大长度，默认为10
 * @returns {string} 格式化后的标签名称
 */
export function formatTagName(tagName, maxLength = 10) {
  if (!tagName) return ''
  
  return truncateText(tagName, maxLength)
}

/**
 * 格式化分类名称
 * @param {string} categoryName - 分类名称
 * @param {number} maxLength - 最大长度，默认为15
 * @returns {string} 格式化后的分类名称
 */
export function formatCategoryName(categoryName, maxLength = 15) {
  if (!categoryName) return ''
  
  return truncateText(categoryName, maxLength)
}

/**
 * 格式化文章标题
 * @param {string} title - 文章标题
 * @param {number} maxLength - 最大长度，默认为50
 * @returns {string} 格式化后的文章标题
 */
export function formatPostTitle(title, maxLength = 50) {
  if (!title) return ''
  
  return truncateText(title, maxLength)
}

/**
 * 格式化IP地址
 * @param {string} ip - IP地址
 * @returns {string} 格式化后的IP地址
 */
export function formatIp(ip) {
  if (!ip) return ''
  
  // 如果是IPv6地址，进行简化显示
  if (ip.includes(':')) {
    return ip.length > 20 ? ip.slice(0, 20) + '...' : ip
  }
  
  return ip
}

/**
 * 格式化User Agent
 * @param {string} userAgent - User Agent字符串
 * @returns {string} 格式化后的User Agent字符串
 */
export function formatUserAgent(userAgent, maxLength = 50) {
  if (!userAgent) return ''
  
  return truncateText(userAgent, maxLength)
}

/**
 * 清理HTML标签
 * @param {string} html - HTML字符串
 * @returns {string} 清理后的纯文本字符串
 */
export function stripHtml(html) {
  if (!html) return ''
  
  return html.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim()
}

/**
 * 转义HTML特殊字符
 * @param {string} text - 文本字符串
 * @returns {string} 转义后的字符串
 */
export function escapeHtml(text) {
  if (!text) return ''
  
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  }
  
  return text.replace(/[&<>"']/g, (m) => map[m])
}

/**
 * 反转义HTML特殊字符
 * @param {string} text - HTML字符串
 * @returns {string} 反转义后的字符串
 */
export function unescapeHtml(text) {
  if (!text) return ''
  
  const map = {
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&quot;': '"',
    '&#39;': "'",
    '&nbsp;': ' '
  }
  
  return text.replace(/&amp;|&lt;|&gt;|&quot;|&#39;|&nbsp;/g, (m) => map[m])
}

/**
 * 生成随机颜色
 * @returns {string} 随机颜色字符串
 */
export function generateRandomColor() {
  const colors = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57',
    '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43',
    '#10AC84', '#EE5A24', '#0984E3', '#6C5CE7', '#A29BFE'
  ]
  
  return colors[Math.floor(Math.random() * colors.length)]
}

/**
 * 生成UUID
 * @returns {string} UUID字符串
 */
export function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

/**
 * 防抖函数
 * @param {Function} func - 要防抖的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, wait) {
  let timeout
  
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * 节流函数
 * @param {Function} func - 要节流的函数
 * @param {number} limit - 限制时间（毫秒）
 * @returns {Function} 节流后的函数
 */
export function throttle(func, limit) {
  let inThrottle
  
  return function() {
    const args = arguments
    const context = this
    
    if (!inThrottle) {
      func.apply(context, args)
      inThrottle = true
      
      setTimeout(() => {
        inThrottle = false
      }, limit)
    }
  }
}

/**
 * 深拷贝对象
 * @param {Object} obj - 要拷贝的对象
 * @returns {Object} 拷贝后的对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  
  if (obj instanceof Date) return new Date(obj.getTime())
  
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  
  if (typeof obj === 'object') {
    const clonedObj = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
}

/**
 * 检查对象是否为空
 * @param {Object} obj - 要检查的对象
 * @returns {boolean} 是否为空
 */
export function isEmptyObject(obj) {
  return obj && Object.keys(obj).length === 0 && obj.constructor === Object
}

/**
 * 检查数组是否为空
 * @param {Array} arr - 要检查的数组
 * @returns {boolean} 是否为空
 */
export function isEmptyArray(arr) {
  return !arr || !Array.isArray(arr) || arr.length === 0
}

/**
 * 检查字符串是否为空
 * @param {string} str - 要检查的字符串
 * @returns {boolean} 是否为空
 */
export function isEmptyString(str) {
  return !str || typeof str !== 'string' || str.trim().length === 0
}

/**
 * 检查值是否为空
 * @param {*} value - 要检查的值
 * @returns {boolean} 是否为空
 */
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  
  if (typeof value === 'string') return isEmptyString(value)
  
  if (Array.isArray(value)) return isEmptyArray(value)
  
  if (typeof value === 'object') return isEmptyObject(value)
  
  return false
}

/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否有效
 */
export function validateEmail(email) {
  if (!email || typeof email !== 'string') return false
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证URL格式
 * @param {string} url - URL字符串
 * @returns {boolean} 是否有效
 */
export function validateUrl(url) {
  if (!url || typeof url !== 'string') return false
  
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

/**
 * 验证手机号格式
 * @param {string} phone - 手机号
 * @returns {boolean} 是否有效
 */
export function validatePhone(phone) {
  if (!phone || typeof phone !== 'string') return false
  
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

/**
 * 验证身份证号格式
 * @param {string} idCard - 身份证号
 * @returns {boolean} 是否有效
 */
export function validateIdCard(idCard) {
  if (!idCard || typeof idCard !== 'string') return false
  
  const idCardRegex = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/
  return idCardRegex.test(idCard)
}

/**
 * 验证用户名格式
 * @param {string} username - 用户名
 * @returns {boolean} 是否有效
 */
export function validateUsername(username) {
  if (!username || typeof username !== 'string') return false
  
  const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/
  return usernameRegex.test(username)
}

/**
 * 验证密码强度
 * @param {string} password - 密码
 * @returns {boolean} 是否有效
 */
export function validatePassword(password) {
  if (!password || typeof password !== 'string') return false
  
  // 至少8个字符，包含大小写字母、数字和特殊字符
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]).{8,}$/
  return passwordRegex.test(password)
}

/**
 * 生成随机字符串
 * @param {number} length - 字符串长度
 * @returns {string} 随机字符串
 */
export function generateRandomString(length = 8) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  
  return result
}

/**
 * 生成随机数字
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {number} 随机数字
 */
export function generateRandomNumber(min = 0, max = 100) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

/**
 * 数组去重
 * @param {Array} arr - 数组
 * @returns {Array} 去重后的数组
 */
export function uniqueArray(arr) {
  if (!Array.isArray(arr)) return []
  
  return [...new Set(arr)]
}

/**
 * 数组扁平化
 * @param {Array} arr - 数组
 * @returns {Array} 扁平化后的数组
 */
export function flattenArray(arr) {
  if (!Array.isArray(arr)) return []
  
  return arr.flat(Infinity)
}

/**
 * 获取数组交集
 * @param {Array} arr1 - 数组1
 * @param {Array} arr2 - 数组2
 * @returns {Array} 交集数组
 */
export function intersection(arr1, arr2) {
  if (!Array.isArray(arr1) || !Array.isArray(arr2)) return []
  
  return arr1.filter(item => arr2.includes(item))
}

/**
 * 获取数组差集
 * @param {Array} arr1 - 数组1
 * @param {Array} arr2 - 数组2
 * @returns {Array} 差集数组
 */
export function difference(arr1, arr2) {
  if (!Array.isArray(arr1) || !Array.isArray(arr2)) return []
  
  return arr1.filter(item => !arr2.includes(item))
}

/**
 * 数组分组
 * @param {Array} arr - 数组
 * @param {Function} keyFn - 分组函数
 * @returns {Object} 分组后的对象
 */
export function groupBy(arr, keyFn) {
  if (!Array.isArray(arr) || typeof keyFn !== 'function') return {}
  
  return arr.reduce((groups, item) => {
    const key = keyFn(item)
    if (!groups[key]) {
      groups[key] = []
    }
    groups[key].push(item)
    return groups
  }, {})
}

/**
 * 数组排序
 * @param {Array} arr - 数组
 * @param {string|Function} key - 排序键或排序函数
 * @param {string} order - 排序顺序，'asc'或'desc'，默认为'asc'
 * @returns {Array} 排序后的数组
 */
export function sortBy(arr, key, order = 'asc') {
  if (!Array.isArray(arr)) return []
  
  const sorted = [...arr]
  
  if (typeof key === 'function') {
    sorted.sort(key)
  } else if (typeof key === 'string') {
    sorted.sort((a, b) => {
      const aVal = a[key]
      const bVal = b[key]
      
      if (aVal < bVal) return order === 'asc' ? -1 : 1
      if (aVal > bVal) return order === 'asc' ? 1 : -1
      return 0
    })
  }
  
  return sorted
}

/**
 * 查找数组中的最大值
 * @param {Array} arr - 数组
 * @param {string|Function} key - 键或函数
 * @returns {*} 最大值
 */
export function maxBy(arr, key) {
  if (!Array.isArray(arr) || arr.length === 0) return undefined
  
  if (typeof key === 'function') {
    return arr.reduce((max, item) => key(item) > key(max) ? item : max)
  } else if (typeof key === 'string') {
    return arr.reduce((max, item) => item[key] > max[key] ? item : max)
  }
  
  return Math.max(...arr)
}

/**
 * 查找数组中的最小值
 * @param {Array} arr - 数组
 * @param {string|Function} key - 键或函数
 * @returns {*} 最小值
 */
export function minBy(arr, key) {
  if (!Array.isArray(arr) || arr.length === 0) return undefined
  
  if (typeof key === 'function') {
    return arr.reduce((min, item) => key(item) < key(min) ? item : min)
  } else if (typeof key === 'string') {
    return arr.reduce((min, item) => item[key] < min[key] ? item : min)
  }
  
  return Math.min(...arr)
}

/**
 * 计算数组平均值
 * @param {Array} arr - 数组
 * @returns {number} 平均值
 */
export function average(arr) {
  if (!Array.isArray(arr) || arr.length === 0) return 0
  
  const sum = arr.reduce((acc, val) => acc + val, 0)
  return sum / arr.length
}

/**
 * 计算数组总和
 * @param {Array} arr - 数组
 * @returns {number} 总和
 */
export function sum(arr) {
  if (!Array.isArray(arr)) return 0
  
  return arr.reduce((acc, val) => acc + val, 0)
}

/**
 * 对象转URL参数
 * @param {Object} params - 参数对象
 * @returns {string} URL参数字符串
 */
export function objectToQueryString(params) {
  if (!params || typeof params !== 'object') return ''
  
  const queryString = Object.keys(params)
    .filter(key => params[key] !== null && params[key] !== undefined && params[key] !== '')
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&')
  
  return queryString ? `?${queryString}` : ''
}

/**
 * URL参数转对象
 * @param {string} queryString - URL参数字符串
 * @returns {Object} 参数对象
 */
export function queryStringToObject(queryString) {
  if (!queryString) return {}
  
  const params = {}
  const queries = queryString.replace(/\?/, '').split('&')
  
  queries.forEach(query => {
    const [key, value] = query.split('=')
    if (key && value) {
      params[decodeURIComponent(key)] = decodeURIComponent(value)
    }
  })
  
  return params
}

/**
 * 下载文件
 * @param {string} url - 文件URL
 * @param {string} filename - 文件名
 */
export function downloadFile(url, filename) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename || ''
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 复制到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise} Promise对象
 */
export function copyToClipboard(text) {
  if (!text) return Promise.reject(new Error('Text is empty'))
  
  if (navigator.clipboard) {
    return navigator.clipboard.writeText(text)
  } else {
    // 兼容旧浏览器
    const textArea = document.createElement('textarea')
    textArea.value = text
    document.body.appendChild(textArea)
    textArea.select()
    
    try {
      document.execCommand('copy')
      document.body.removeChild(textArea)
      return Promise.resolve()
    } catch (err) {
      document.body.removeChild(textArea)
      return Promise.reject(err)
    }
  }
}

/**
 * 获取文件扩展名
 * @param {string} filename - 文件名
 * @returns {string} 文件扩展名
 */
export function getFileExtension(filename) {
  if (!filename || typeof filename !== 'string') return ''
  
  const parts = filename.split('.')
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : ''
}

/**
 * 检查文件类型是否为图片
 * @param {string} filename - 文件名
 * @returns {boolean} 是否为图片
 */
export function isImageFile(filename) {
  const ext = getFileExtension(filename)
  const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp']
  return imageExts.includes(ext)
}

/**
 * 检查文件类型是否为视频
 * @param {string} filename - 文件名
 * @returns {boolean} 是否为视频
 */
export function isVideoFile(filename) {
  const ext = getFileExtension(filename)
  const videoExts = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
  return videoExts.includes(ext)
}

/**
 * 检查文件类型是否为音频
 * @param {string} filename - 文件名
 * @returns {boolean} 是否为音频
 */
export function isAudioFile(filename) {
  const ext = getFileExtension(filename)
  const audioExts = ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma']
  return audioExts.includes(ext)
}

/**
 * 检查文件类型是否为文档
 * @param {string} filename - 文件名
 * @returns {boolean} 是否为文档
 */
export function isDocumentFile(filename) {
  const ext = getFileExtension(filename)
  const docExts = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt']
  return docExts.includes(ext)
}