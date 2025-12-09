import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/utils/api'

export const usePostsStore = defineStore('posts', () => {
  const toast = useToast()
  
  // 状态
  const posts = ref([])
  const currentPost = ref(null)
  const loading = ref(false)
  const pagination = ref({
    page: 1,
    per_page: 10,
    total: 0,
    pages: 1
  })
  
  // 计算属性
  const hasMorePosts = computed(() => pagination.value.page < pagination.value.pages)
  const isEmpty = computed(() => (posts.value || []).length === 0)
  
  // 获取文章列表
  const fetchPosts = async (params = {}) => {
    loading.value = true
    try {
      const endpoint = params.mine ? '/posts/mine' : '/posts'
      const { mine, ...rest } = params
      const response = await api.get(endpoint, { params: rest })
      const { posts: postsData, pagination: paginationData } = response.data
      
      if (params.page && params.page > 1) {
        // 如果是加载更多，追加到现有列表
        posts.value.push(...postsData)
      } else {
        // 否则替换现有列表
        posts.value = postsData
      }
      
      pagination.value = paginationData
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || '获取文章列表失败'
      toast.error(message)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 获取单篇文章
  const fetchPost = async (postId) => {
    loading.value = true
    try {
      const response = await api.get(`/posts/${postId}`)
      currentPost.value = response.data.post
      return response.data.post
    } catch (error) {
      const message = error.response?.data?.message || '获取文章详情失败'
      toast.error(message)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 创建文章
  const createPost = async (postData) => {
    loading.value = true
    try {
      const response = await api.post('/posts', postData)
      const newPost = response.data.post
      
      // 添加到文章列表开头
      posts.value.unshift(newPost)
      
      toast.success('文章发布成功')
      return newPost
    } catch (error) {
      const message = error.response?.data?.message || '发布文章失败'
      toast.error(message)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 更新文章
  const updatePost = async (postId, postData) => {
    loading.value = true
    try {
      const response = await api.put(`/posts/${postId}`, postData)
      const updatedPost = response.data.post
      
      // 更新文章列表中的文章
      const index = posts.value.findIndex(post => post.id === postId)
      if (index !== -1) {
        posts.value[index] = updatedPost
      }
      
      // 更新当前文章
      if (currentPost.value?.id === postId) {
        currentPost.value = updatedPost
      }
      
      toast.success('文章更新成功')
      return updatedPost
    } catch (error) {
      const message = error.response?.data?.message || '更新文章失败'
      toast.error(message)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 删除文章
  const deletePost = async (postId) => {
    loading.value = true
    try {
      await api.delete(`/posts/${postId}`)
      
      // 从文章列表中移除
      posts.value = posts.value.filter(post => post.id !== postId)
      
      // 如果删除的是当前文章，清空当前文章
      if (currentPost.value?.id === postId) {
        currentPost.value = null
      }
      
      toast.success('文章删除成功')
    } catch (error) {
      const message = error.response?.data?.message || '删除文章失败'
      toast.error(message)
      throw error
    } finally {
      loading.value = false
    }
  }
  
  // 点赞文章
  const likePost = async (postId) => {
    try {
      const response = await api.post(`/posts/${postId}/like`)
      const { liked, like_count } = response.data
      
      // 更新文章列表中的点赞状态
      const index = posts.value.findIndex(post => post.id === postId)
      if (index !== -1) {
        posts.value[index].liked = liked
        posts.value[index].like_count = like_count
      }
      
      // 更新当前文章的点赞状态
      if (currentPost.value?.id === postId) {
        currentPost.value.liked = liked
        currentPost.value.like_count = like_count
      }
      
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || '操作失败'
      toast.error(message)
      throw error
    }
  }
  
  // 收藏文章
  const favoritePost = async (postId) => {
    try {
      const response = await api.post(`/posts/${postId}/favorite`)
      const { favorited, favorite_count } = response.data
      
      // 更新文章列表中的收藏状态
      const index = posts.value.findIndex(post => post.id === postId)
      if (index !== -1) {
        posts.value[index].favorited = favorited
        posts.value[index].favorite_count = favorite_count
      }
      
      // 更新当前文章的收藏状态
      if (currentPost.value?.id === postId) {
        currentPost.value.favorited = favorited
        currentPost.value.favorite_count = favorite_count
      }
      
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || '操作失败'
      toast.error(message)
      throw error
    }
  }

  // 兼容旧调用名
  const toggleLike = async (postId) => likePost(postId)
  const toggleFavorite = async (postId) => favoritePost(postId)
  
  // 获取热门文章
  const fetchPopularPosts = async (params = {}) => {
    try {
      const response = await api.get('/posts/popular', { params })
      return response.data.posts
    } catch (error) {
      const message = error.response?.data?.message || '获取热门文章失败'
      toast.error(message)
      throw error
    }
  }
  
  // 获取推荐文章
  const fetchFeaturedPosts = async (params = {}) => {
    try {
      const response = await api.get('/posts/featured', { params })
      return response.data.posts
    } catch (error) {
      const message = error.response?.data?.message || '获取推荐文章失败'
      toast.error(message)
      throw error
    }
  }
  
  // 获取文章归档
  const fetchArchives = async () => {
    try {
      const response = await api.get('/posts/archives')
      return response.data.archives
    } catch (error) {
      const message = error.response?.data?.message || '获取归档失败'
      toast.error(message)
      throw error
    }
  }
  
  // 获取搜索建议
  const getSearchSuggestions = async (query) => {
    try {
      const response = await api.get('/posts/search/suggestions', {
        params: { q: query }
      })
      return response.data.suggestions
    } catch (error) {
      console.error('Get search suggestions error:', error)
      return []
    }
  }
  
  // 加载更多文章
  const loadMorePosts = async (params = {}) => {
    if (hasMorePosts.value && !loading.value) {
      const nextPage = pagination.value.page + 1
      await fetchPosts({ ...params, page: nextPage })
    }
  }
  
  // 清空文章列表
  const clearPosts = () => {
    posts.value = []
    currentPost.value = null
    pagination.value = {
      page: 1,
      per_page: 10,
      total: 0,
      pages: 1
    }
  }
  
  // 设置当前文章
  const setCurrentPost = (post) => {
    currentPost.value = post
  }
  
  // 清除当前文章
  const clearCurrentPost = () => {
    currentPost.value = null
  }
  
  return {
    posts,
    currentPost,
    loading,
    pagination,
    hasMorePosts,
    isEmpty,
    fetchPosts,
    fetchPost,
    createPost,
    updatePost,
    deletePost,
    likePost,
    favoritePost,
    toggleLike,
    toggleFavorite,
    fetchPopularPosts,
    fetchFeaturedPosts,
    fetchArchives,
    getSearchSuggestions,
    loadMorePosts,
    clearPosts,
    setCurrentPost,
    clearCurrentPost
  }
})