<template>
  <div class="cassette-categories-terminal">
    <div class="categories-container">
      <!-- 页面头部 -->
      <header class="categories-header">
        <div class="header-title">
          <h1>CATEGORY ARCHIVE</h1>
          <p>BROWSE BY CATEGORIES</p>
        </div>
      </header>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-skeleton">
          <div v-for="i in 6" :key="i" class="skeleton-card"></div>
        </div>
      </div>

      <div v-else-if="categories.length > 0" class="categories-content">
        <!-- 分类列表 -->
        <section class="categories-list-section">
          <div class="section-header">
            <span class="section-label">CATEGORIES LIST</span>
          </div>
          <div class="categories-grid">
            <div
              v-for="category in categories"
              :key="category.id"
              class="category-card"
              @click="goToCategory(category.slug)"
            >
              <div class="category-icon">
                <span class="icon">📁</span>
              </div>
              <div class="category-info">
                <h3>{{ category.name }}</h3>
                <p class="category-desc">
                  {{ category.description || "NO DESCRIPTION" }}
                </p>
              </div>
              <div class="category-stats">
                <div class="stat-item">
                  <span class="stat-number">{{ category.post_count }}</span>
                  <span class="stat-label">ARTICLES</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{
                    category.view_count || 0
                  }}</span>
                  <span class="stat-label">VIEWS</span>
                </div>
              </div>
              <div class="category-action">
                <span class="action-icon">→</span>
              </div>
            </div>
          </div>
        </section>

        <!-- 分类统计 -->
        <section class="categories-stats-section">
          <div class="section-header">
            <span class="section-label">CATEGORY STATISTICS</span>
          </div>
          <div class="stats-card">
            <div class="stats-grid">
              <div class="stat-card">
                <div class="stat-icon">
                  <span class="icon">📁</span>
                </div>
                <div class="stat-content">
                  <span class="stat-number">{{ categories.length }}</span>
                  <span class="stat-label">TOTAL CATEGORIES</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">
                  <span class="icon">📄</span>
                </div>
                <div class="stat-content">
                  <span class="stat-number">{{ totalPosts }}</span>
                  <span class="stat-label">TOTAL ARTICLES</span>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">
                  <span class="icon">👁️</span>
                </div>
                <div class="stat-content">
                  <span class="stat-number">{{ totalViews }}</span>
                  <span class="stat-label">TOTAL VIEWS</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-console">
          <div class="empty-icon">📁</div>
          <div class="empty-text">NO CATEGORIES FOUND</div>
          <div class="empty-subtext">ARCHIVE EMPTY</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { Folder, ArrowRight, Document, View } from "@element-plus/icons-vue";

const router = useRouter();

const loading = ref(false);
const categories = ref([]);

const totalPosts = computed(() => {
  return (categories.value || []).reduce(
    (sum, category) => sum + (category.post_count || 0),
    0,
  );
});

const totalViews = computed(() => {
  return (categories.value || []).reduce(
    (sum, category) => sum + (category.view_count || 0),
    0,
  );
});

const goToCategory = (slug) => {
  router.push(`/categories/${slug}`);
};

const fetchCategories = async () => {
  loading.value = true;
  try {
    const response = await fetch("/api/posts/categories");
    const data = await response.json();
    categories.value = data.categories || [];
  } catch (error) {
    console.error("Failed to fetch categories:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchCategories();
});
</script>

<style scoped>
.cassette-categories-terminal {
  position: relative;
  min-height: 100vh;
  background-color: #f5f0e6;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  color: #2c2c2c;
  font-family: "Courier New", monospace;
  overflow: hidden;
}

.categories-container {
  position: relative;
  z-index: 2;
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 页面头部 */
.categories-header {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
  margin-bottom: 40px;
  position: relative;
  text-align: center;
}

.categories-header::before {
  content: "CATEGORY ARCHIVE";
  position: absolute;
  top: -10px;
  left: 10px;
  background: #e67e22;
  color: white;
  padding: 5px 15px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.header-title h1 {
  font-size: 2.5rem;
  font-weight: 900;
  color: #2c2c2c;
  margin: 0 0 10px 0;
  letter-spacing: 3px;
  text-transform: uppercase;
}

.header-title p {
  font-size: 14px;
  color: #2c2c2c;
  opacity: 0.8;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600;
}

/* 加载状态 */
.loading-state {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 40px;
  margin-bottom: 30px;
}

.loading-skeleton {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.skeleton-card {
  height: 120px;
  background: #e0e0e0;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  animation: pulse 1.5s infinite ease-in-out;
}

@keyframes pulse {
  0%,
  100% {
    opacity: 0.7;
  }
  50% {
    opacity: 1;
  }
}

/* 分类内容区域 */
.categories-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* 章节头部 */
.section-header {
  margin-bottom: 25px;
}

.section-label {
  background: #e67e22;
  color: white;
  padding: 8px 15px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 2px 2px 0 #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 分类列表 */
.categories-list-section {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.category-card {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 25px;
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 3px 3px 0 #2c2c2c;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-card:hover {
  box-shadow: 5px 5px 0 #e67e22;
  transform: translate(-2px, -2px);
}

.category-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #e67e22;
  font-size: 28px;
  flex-shrink: 0;
}

.category-icon .icon {
  font-size: 24px;
}

.category-info {
  flex: 1;
  min-width: 0;
}

.category-info h3 {
  margin: 0 0 8px 0;
  font-size: 1.2rem;
  font-weight: 900;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.category-desc {
  margin: 0;
  color: #2c2c2c;
  font-size: 12px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  font-family: "Courier New", monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.category-stats {
  display: flex;
  gap: 16px;
  text-align: center;
  flex-shrink: 0;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 60px;
}

.stat-number {
  font-size: 1.1rem;
  font-weight: 900;
  color: #2c2c2c;
}

.stat-label {
  font-size: 10px;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
  margin-top: 3px;
}

.category-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: #e67e22;
  border: 2px solid #2c2c2c;
  box-shadow: 1px 1px 0 #2c2c2c;
  flex-shrink: 0;
  margin-left: 10px;
}

.action-icon {
  color: white;
  font-weight: 900;
  font-size: 16px;
}

/* 分类统计 */
.categories-stats-section {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
}

.stats-card {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 3px 3px 0 #2c2c2c;
  padding: 30px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 25px;
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: #e67e22;
  border: 2px solid #2c2c2c;
  box-shadow: 1px 1px 0 #2c2c2c;
  font-size: 24px;
  flex-shrink: 0;
}

.stat-icon .icon {
  color: white;
  font-size: 20px;
}

.stat-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.stat-content .stat-number {
  font-size: 1.5rem;
  font-weight: 900;
  color: #2c2c2c;
  margin-bottom: 5px;
}

.stat-content .stat-label {
  font-size: 12px;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

/* 空状态 */
.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.empty-console {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 40px;
  text-align: center;
  max-width: 500px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  color: #e67e22;
}

.empty-text {
  font-size: 24px;
  font-weight: 900;
  color: #2c2c2c;
  margin-bottom: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.empty-subtext {
  font-size: 14px;
  color: #2c2c2c;
  opacity: 0.7;
  font-family: "Courier New", monospace;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-weight: 600;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .categories-container {
    padding: 20px 15px;
  }

  .categories-header,
  .categories-list-section,
  .categories-stats-section {
    padding: 20px;
  }

  .header-title h1 {
    font-size: 2rem;
  }

  .categories-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .category-card {
    flex-direction: column;
    text-align: center;
  }

  .category-stats {
    justify-content: center;
    margin: 15px 0;
  }

  .category-action {
    margin-left: 0;
  }
}

@media (max-width: 480px) {
  .header-title h1 {
    font-size: 1.5rem;
  }

  .category-card,
  .stat-card {
    padding: 20px;
  }

  .category-info h3 {
    font-size: 1rem;
  }

  .stat-content .stat-number {
    font-size: 1.2rem;
  }
}
</style>
