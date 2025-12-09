<template>
  <div class="tag-detail" v-loading="loading">
    <div class="container">
      <div class="page-header">
        <div>
          <p class="breadcrumb">标签</p>
          <h1>#{{ tagInfo?.name || route.params.slug }}</h1>
          <p class="description">{{ tagInfo?.description || '与该标签相关的文章' }}</p>
        </div>
        <el-tag type="info">{{ postsStore.pagination.total }} 篇文章</el-tag>
      </div>

      <div v-if="posts.length" class="posts-list">
        <PostItem v-for="p in posts" :key="p.id" :post="p" />
      </div>
      <el-empty v-else description="暂无相关文章" />
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
const tagInfo = ref(null)
const posts = computed(() => postsStore.posts)

const fetchTagInfo = async () => {
  const res = await fetch('/api/posts/tags')
  const data = await res.json()
  tagInfo.value = (data.tags || []).find((t) => t.slug === route.params.slug)
}

const fetchPosts = async () => {
  loading.value = true
  try {
    await postsStore.fetchPosts({ tag: route.params.slug, per_page: 20 })
  } catch (error) {
    console.error('加载标签文章失败', error)
  } finally {
    loading.value = false
  }
}

const loadData = async () => {
  await Promise.all([fetchTagInfo(), fetchPosts()])
}

onMounted(loadData)

watch(
  () => route.params.slug,
  () => loadData()
)
</script>

<style scoped>
.tag-detail {
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
