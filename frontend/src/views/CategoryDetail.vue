<template>
  <div class="category-detail" v-loading="loading">
    <div class="container">
      <div class="page-header">
        <div>
          <p class="breadcrumb">分类</p>
          <h1>{{ categoryInfo?.name || route.params.slug }}</h1>
          <p class="description">{{ categoryInfo?.description || '分类下的文章列表' }}</p>
        </div>
        <el-tag type="success">{{ postsStore.pagination.total }} 篇文章</el-tag>
      </div>

      <div v-if="posts.length" class="posts-list">
        <PostItem v-for="p in posts" :key="p.id" :post="p" />
      </div>
      <el-empty v-else description="该分类暂无文章" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import PostItem from '@/components/posts/PostItem.vue'
import { usePostsStore } from '@/stores/posts'

const route = useRoute()
const postsStore = usePostsStore()
const loading = ref(false)
const categoryInfo = ref(null)
const posts = computed(() => postsStore.posts)

const fetchCategoryInfo = async () => {
  const res = await fetch('/api/posts/categories')
  const data = await res.json()
  categoryInfo.value = (data.categories || []).find((c) => c.slug === route.params.slug)
}

const fetchPosts = async () => {
  loading.value = true
  try {
    await postsStore.fetchPosts({ category: route.params.slug, per_page: 20 })
  } catch (error) {
    console.error('加载分类文章失败', error)
  } finally {
    loading.value = false
  }
}

const loadData = async () => {
  await Promise.all([fetchCategoryInfo(), fetchPosts()])
}

onMounted(loadData)

watch(
  () => route.params.slug,
  () => loadData()
)
</script>

<style scoped>
.category-detail {
  min-height: 100vh;
  padding: 32px 0;
  background: var(--el-bg-color-page);
}
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.breadcrumb {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
.description {
  margin: 4px 0 0;
  color: var(--el-text-color-secondary);
}
.posts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
