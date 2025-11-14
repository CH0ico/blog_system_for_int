<template>
  <div class="tags-page">
    <div class="container">
      <div class="page-header">
        <h1>标签云</h1>
        <p>通过标签发现感兴趣的内容</p>
      </div>
      
      <div v-if="loading" class="loading-state">
        <el-loading :loading="true" text="加载中..." />
      </div>
      
      <div v-else-if="tags.length > 0" class="tags-container">
        <div class="tag-cloud">
          <div
            v-for="tag in tags"
            :key="tag.id"
            class="tag-item"
            :style="{ fontSize: getTagSize(tag.post_count) + 'px' }"
            @click="goToTag(tag.slug)"
          >
            <span class="tag-name">{{ tag.name }}</span>
            <span class="tag-count">({{ tag.post_count }})</span>
          </div>
        </div>
        
        <!-- 热门标签 -->
        <div class="popular-tags">
          <h3>热门标签</h3>
          <div class="popular-tags-grid">
            <div
              v-for="tag in popularTags"
              :key="tag.id"
              class="popular-tag-card"
              @click="goToTag(tag.slug)"
            >
              <div class="tag-icon">
                <el-icon><CollectionTag /></el-icon>
              </div>
              <div class="tag-info">
                <h4>{{ tag.name }}</h4>
                <p>{{ tag.post_count }} 篇文章</p>
              </div>
              <div class="tag-arrow">
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <el-empty description="暂无标签" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CollectionTag, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const tags = ref([])

const popularTags = computed(() => {
  return [...tags.value]
    .sort((a, b) => b.post_count - a.post_count)
    .slice(0, 6)
})

const getTagSize = (postCount) => {
  const minSize = 12
  const maxSize = 24
  // 确保tags存在且有数据
  const validTags = tags.value || []
  if (validTags.length === 0) return minSize
  
  const maxCount = Math.max(...validTags.map(t => t.post_count || 0), 1)
  const ratio = postCount / maxCount
  return Math.max(minSize, Math.min(maxSize, minSize + (maxSize - minSize) * ratio))
}

const goToTag = (slug) => {
  router.push(`/tags/${slug}`)
}

const fetchTags = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/posts/tags')
    const data = await response.json()
    tags.value = data.tags || []
  } catch (error) {
    console.error('Failed to fetch tags:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchTags()
})
</script>

<style scoped>
.tags-page {
  min-height: 100vh;
  padding: 40px 0;
  background-color: var(--el-bg-color-page);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-header h1 {
  margin: 0 0 16px 0;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.page-header p {
  margin: 0;
  font-size: 1.1rem;
  color: var(--el-text-color-secondary);
}

.tags-container {
  margin-top: 20px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
  margin-bottom: 60px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  background: var(--el-fill-color-light);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.tag-item:hover {
  background: var(--el-color-primary);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.tag-name {
  font-weight: 500;
}

.tag-count {
  font-size: 0.9em;
  opacity: 0.8;
}

.popular-tags {
  margin-top: 40px;
}

.popular-tags h3 {
  margin: 0 0 24px 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
  text-align: center;
}

.popular-tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.popular-tag-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.popular-tag-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.tag-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--el-color-primary-light-9);
  border-radius: 50%;
  color: var(--el-color-primary);
  font-size: 20px;
}

.tag-info {
  flex: 1;
}

.tag-info h4 {
  margin: 0 0 4px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.tag-info p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.tag-arrow {
  color: var(--el-text-color-secondary);
  font-size: 16px;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-skeleton {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}

@media (max-width: 768px) {
  .tag-cloud {
    padding: 20px;
  }
  
  .popular-tags-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header h1 {
    font-size: 2rem;
  }
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .tag-item {
    padding: 6px 12px;
  }
  
  .popular-tag-card {
    padding: 16px;
  }
}
</style>