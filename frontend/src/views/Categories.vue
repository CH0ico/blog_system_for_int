<template>
  <div class="categories-page">
    <div class="container">
      <div class="page-header">
        <h1>文章分类</h1>
        <p>按分类浏览文章</p>
      </div>
      
      <div v-if="loading" class="loading-state">
        <el-loading :loading="true" text="加载中..." />
      </div>
      
      <div v-else-if="categories.length > 0" class="categories-container">
        <div class="categories-grid">
          <div
            v-for="category in categories"
            :key="category.id"
            class="category-card"
            @click="goToCategory(category.slug)"
          >
            <div class="category-icon">
              <el-icon><Folder /></el-icon>
            </div>
            <div class="category-info">
              <h3>{{ category.name }}</h3>
              <p>{{ category.description || '暂无描述' }}</p>
            </div>
            <div class="category-stats">
              <div class="stat-item">
                <span class="stat-number">{{ category.post_count }}</span>
                <span class="stat-label">文章</span>
              </div>
              <div class="stat-item">
                <span class="stat-number">{{ category.view_count || 0 }}</span>
                <span class="stat-label">浏览</span>
              </div>
            </div>
            <div class="category-arrow">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
        
        <!-- 分类统计 -->
        <div class="categories-stats">
          <div class="stats-card">
            <h3>分类统计</h3>
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><Folder /></el-icon>
                </div>
                <div class="stat-content">
                  <span class="stat-number">{{ categories.length }}</span>
                  <span class="stat-label">总分类数</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><Document /></el-icon>
                </div>
                <div class="stat-content">
                  <span class="stat-number">{{ totalPosts }}</span>
                  <span class="stat-label">总文章数</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">
                  <el-icon><View /></el-icon>
                </div>
                <div class="stat-content">
                  <span class="stat-number">{{ totalViews }}</span>
                  <span class="stat-label">总浏览量</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-state">
        <el-empty description="暂无分类" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Folder, ArrowRight, Document, View } from '@element-plus/icons-vue'

const router = useRouter()

const loading = ref(false)
const categories = ref([])

const totalPosts = computed(() => {
  return (categories.value || []).reduce((sum, category) => sum + (category.post_count || 0), 0)
})

const totalViews = computed(() => {
  return (categories.value || []).reduce((sum, category) => sum + (category.view_count || 0), 0)
})

const goToCategory = (slug) => {
  router.push(`/categories/${slug}`)
}

const fetchCategories = async () => {
  loading.value = true
  try {
    const response = await fetch('/api/posts/categories')
    const data = await response.json()
    categories.value = data.categories || []
  } catch (error) {
    console.error('Failed to fetch categories:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.categories-page {
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

.categories-container {
  margin-top: 20px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.category-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.category-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: var(--el-color-primary-light-9);
  border-radius: 12px;
  color: var(--el-color-primary);
  font-size: 24px;
  flex-shrink: 0;
}

.category-info {
  flex: 1;
  min-width: 0;
}

.category-info h3 {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.category-info p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.category-stats {
  display: flex;
  gap: 16px;
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.category-arrow {
  color: var(--el-text-color-secondary);
  font-size: 16px;
  margin-left: 8px;
}

.categories-stats {
  margin-top: 40px;
}

.stats-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stats-card h3 {
  margin: 0 0 24px 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
  text-align: center;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--el-fill-color-lighter);
  border-radius: 8px;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: var(--el-color-primary-light-8);
  border-radius: 50%;
  color: var(--el-color-primary);
  font-size: 20px;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-content .stat-number {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.stat-content .stat-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.loading-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

@media (max-width: 768px) {
  .categories-grid {
    grid-template-columns: 1fr;
  }
  
  .category-card {
    flex-direction: column;
    text-align: center;
  }
  
  .category-stats {
    justify-content: center;
  }
  
  .stats-grid {
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
  
  .category-card {
    padding: 20px;
  }
  
  .category-icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }
  
  .stats-card {
    padding: 24px;
  }
}
</style>