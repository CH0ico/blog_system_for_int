<template>
  <div class="cassette-tags-terminal">
    <div class="tags-container">
      <!-- 页面头部 -->
      <header class="tags-header">
        <div class="header-title">
          <h1>TAG DATABASE</h1>
          <p>NAVIGATE BY TOPICS</p>
        </div>
      </header>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-skeleton">
          <div v-for="i in 12" :key="i" class="skeleton-tag"></div>
        </div>
      </div>

      <!-- 标签内容 -->
      <div v-else-if="tags.length > 0" class="tags-content">
        <!-- 标签云 -->
        <section class="tag-cloud-section">
          <div class="section-header">
            <span class="section-label">TAG CLOUD</span>
          </div>
          <div class="tag-cloud">
            <div
              v-for="tag in tags"
              :key="tag.id"
              class="tag-item"
              :style="{ fontSize: getTagSize(tag.post_count) + 'px' }"
              @click="goToTag(tag.slug)"
            >
              <span class="tag-name">#{{ tag.name }}</span>
              <span class="tag-count">({{ tag.post_count }})</span>
            </div>
          </div>
        </section>

        <!-- 热门标签 -->
        <section class="popular-tags-section">
          <div class="section-header">
            <span class="section-label">POPULAR TAGS</span>
          </div>
          <div class="popular-tags-grid">
            <div
              v-for="tag in popularTags"
              :key="tag.id"
              class="popular-tag-card"
              @click="goToTag(tag.slug)"
            >
              <div class="tag-icon">
                <span class="icon">🏷️</span>
              </div>
              <div class="tag-info">
                <h4>{{ tag.name }}</h4>
                <p>{{ tag.post_count }} ARTICLES</p>
              </div>
              <div class="tag-action">
                <span class="action-icon">→</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-console">
          <div class="empty-icon">📛</div>
          <div class="empty-text">NO TAGS FOUND</div>
          <div class="empty-subtext">DATABASE EMPTY</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { CollectionTag, ArrowRight } from "@element-plus/icons-vue";

const router = useRouter();

const loading = ref(false);
const tags = ref([]);

const popularTags = computed(() => {
  return [...tags.value]
    .sort((a, b) => b.post_count - a.post_count)
    .slice(0, 6);
});

const getTagSize = (postCount) => {
  const minSize = 12;
  const maxSize = 24;
  // 确保tags存在且有数据
  const validTags = tags.value || [];
  if (validTags.length === 0) return minSize;

  const maxCount = Math.max(...validTags.map((t) => t.post_count || 0), 1);
  const ratio = postCount / maxCount;
  return Math.max(
    minSize,
    Math.min(maxSize, minSize + (maxSize - minSize) * ratio),
  );
};

const goToTag = (slug) => {
  router.push(`/tags/${slug}`);
};

const fetchTags = async () => {
  loading.value = true;
  try {
    const response = await fetch("/api/posts/tags");
    const data = await response.json();
    tags.value = data.tags || [];
  } catch (error) {
    console.error("Failed to fetch tags:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchTags();
});
</script>

<style scoped>
.cassette-tags-terminal {
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

.tags-container {
  position: relative;
  z-index: 2;
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 页面头部 */
.tags-header {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
  margin-bottom: 40px;
  position: relative;
  text-align: center;
}

.tags-header::before {
  content: "TAG DATABASE";
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
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}

.skeleton-tag {
  width: 80px;
  height: 30px;
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

/* 标签内容区域 */
.tags-content {
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

/* 标签云区域 */
.tag-cloud-section {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  justify-content: center;
  min-height: 200px;
  align-items: center;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  cursor: pointer;
  transition: all 0.1s ease;
  font-family: "Courier New", monospace;
  font-weight: 600;
  color: #2c2c2c;
}

.tag-item:hover {
  background: #e67e22;
  color: white;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

.tag-name {
  font-weight: 900;
}

.tag-count {
  font-size: 0.9em;
  opacity: 0.8;
  font-weight: 600;
}

/* 热门标签区域 */
.popular-tags-section {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
}

.popular-tags-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.popular-tag-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 25px;
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 3px 3px 0 #2c2c2c;
  cursor: pointer;
  transition: all 0.2s ease;
}

.popular-tag-card:hover {
  box-shadow: 5px 5px 0 #e67e22;
  transform: translate(-2px, -2px);
}

.tag-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 50px;
  height: 50px;
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #e67e22;
  font-size: 24px;
}

.tag-icon .icon {
  font-size: 20px;
}

.tag-info {
  flex: 1;
}

.tag-info h4 {
  margin: 0 0 5px 0;
  font-size: 1.2rem;
  font-weight: 900;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.tag-info p {
  margin: 0;
  color: #2c2c2c;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tag-action {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  background: #e67e22;
  border: 2px solid #2c2c2c;
  box-shadow: 1px 1px 0 #2c2c2c;
}

.action-icon {
  color: white;
  font-weight: 900;
  font-size: 16px;
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
  .tags-container {
    padding: 20px 15px;
  }

  .tags-header,
  .tag-cloud-section,
  .popular-tags-section {
    padding: 20px;
  }

  .header-title h1 {
    font-size: 2rem;
  }

  .popular-tags-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .header-title h1 {
    font-size: 1.5rem;
  }

  .tag-cloud {
    gap: 10px;
  }

  .tag-item {
    padding: 8px 12px;
    font-size: 12px;
  }

  .popular-tag-card {
    padding: 20px;
  }

  .tag-info h4 {
    font-size: 1rem;
  }
}
</style>
