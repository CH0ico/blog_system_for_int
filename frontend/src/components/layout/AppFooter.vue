<template>
  <el-footer class="app-footer">
    <div class="footer-container">
      <!-- 页脚内容 -->
      <div class="footer-content">
        <!-- 关于网站 -->
        <div class="footer-section">
          <h4>关于博客</h4>
          <p>
            一个现代化的博客系统，采用Vue.js +
            Flask技术栈构建，支持实时通信、社交互动等功能。
          </p>
        </div>

        <!-- 快速链接 -->
        <div class="footer-section">
          <h4>快速链接</h4>
          <ul class="footer-links">
            <li><router-link to="/categories">分类</router-link></li>
            <li><router-link to="/about">关于</router-link></li>
          </ul>
        </div>

        <!-- 技术栈 -->
        <div class="footer-section">
          <h4>技术栈</h4>
          <div class="tech-stack">
            <el-tag>Vue.js 3</el-tag>
            <el-tag>Element Plus</el-tag>
            <el-tag>Flask</el-tag>
            <el-tag>Socket.IO</el-tag>
            <el-tag>JWT</el-tag>
            <el-tag>SQLite/MySQL</el-tag>
          </div>
        </div>

        <!-- 联系信息 -->
        <div class="footer-section">
          <h4>联系我们</h4>
          <div class="contact-info">
            <p>
              <el-icon><Message /></el-icon> contact@blog.com
            </p>
            <p>
              <el-icon><Link /></el-icon> https://blog.example.com
            </p>
          </div>
        </div>
      </div>

    </div>
  </el-footer>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import {
  Message,
  Link,
  User,
  Document,
  CollectionTag,
  Calendar,
  Folder,
  PriceTag,
} from "@element-plus/icons-vue";
import { usePostsStore } from "@/stores/posts";
import { useSocketStore } from "@/stores/socket";

const postsStore = usePostsStore();
const socketStore = useSocketStore();

// 状态
const stats = ref({
  totalPosts: 0,
  runningDays: 0,
});

// 计算属性
const currentYear = computed(() => new Date().getFullYear());
const onlineCount = computed(() => socketStore.onlineCount);

// 获取统计信息
const fetchStats = async () => {
  try {
    // 获取文章总数
    await postsStore.fetchPosts({ per_page: 1 });
    stats.value.totalPosts = postsStore.pagination.total;

    // 计算运行天数（假设从2024年1月1日开始）
    const startDate = new Date("2024-01-01");
    const now = new Date();
    const diffTime = Math.abs(now - startDate);
    stats.value.runningDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  } catch (error) {
    console.error("Failed to fetch stats:", error);
  }
};

onMounted(() => {
  fetchStats();
});
</script>

<style scoped>
/* 工业风页脚基础样式 */
.app-footer {
  background-color: #e6e4d8;
  border-top: 4px solid #111;
  padding: 30px 0 15px;
  margin-top: auto;
  font-size: 14px;
  font-family: 'Courier New', monospace;
  box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.1);
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 页脚内容布局 - 工业风紧凑设计 */
.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
  border: 2px solid #111;
  padding: 20px;
  background: #fff;
  box-shadow: 4px 4px 0 #111;
}

/* 工业风h4标题样式 */
.footer-section h4 {
  margin-bottom: 14px;
  color: #111;
  font-size: 14px;
  font-weight: 700;
  font-family: 'Courier New', monospace;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  position: relative;
  padding: 8px 12px;
  background: #f7931e;
  border: 2px solid #111;
  box-shadow: 3px 3px 0 #111;
}

/* 移除原有的下划线效果，替换为工业风边框 */
.footer-section h4::after {
  display: none;
}

/* 工业风p文本样式 */
.footer-section p {
  color: #111;
  line-height: 1.6;
  margin-bottom: 12px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  background: #f5f5f5;
  padding: 8px;
  border: 1px solid #111;
  box-shadow: 2px 2px 0 #111;
}

/* 快速链接样式 */
.footer-links {
  list-style: none;
  padding: 0;
}

.footer-links li {
  margin-bottom: 10px;
}

.footer-links a {
  color: #111;
  text-decoration: none;
  transition: all 0.2s ease;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  display: inline-block;
  padding: 6px 10px;
  background: #fff;
  border: 2px solid #111;
  box-shadow: 2px 2px 0 #111;
}

.footer-links a:hover {
  color: #f7931e;
  transform: translate(2px, 2px);
  box-shadow: 0 0 0 #111;
}

/* 技术栈标签 - 工业风设计 */
.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tech-stack .el-tag {
  margin: 0;
  font-size: 12px;
  padding: 4px 8px;
  background: #fff;
  color: #111;
  border: 2px solid #111;
  border-radius: 0;
  font-family: 'Courier New', monospace;
  box-shadow: 2px 2px 0 #111;
}

/* 联系信息样式 */
.contact-info p {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.contact-info .el-icon {
  font-size: 14px;
  color: #111;
}

/* 页脚底部样式 - 工业风 */
.footer-bottom {
  border-top: 2px solid #111;
  padding-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  background: #fff;
  padding: 16px;
  border: 2px solid #111;
  box-shadow: 4px 4px 0 #111;
}

.copyright {
  color: #111;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.copyright p {
  margin: 0;
  line-height: 1.4;
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}

/* 统计信息样式 */
.stats {
  display: flex;
  gap: 12px;
  color: #111;
  font-size: 13px;
  font-family: 'Courier New', monospace;
}

.stats span {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: #f7931e;
  border: 2px solid #111;
  box-shadow: 2px 2px 0 #111;
}

/* 响应式设计 - 保持工业风 */
@media (max-width: 768px) {
  .footer-content {
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 20px;
  }

  .footer-bottom {
    flex-direction: column;
    text-align: center;
  }

  .stats {
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .app-footer {
    padding: 20px 0 10px;
  }

  .footer-container {
    padding: 0 16px;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 15px;
  }

  .footer-section h4 {
    font-size: 13px;
    margin-bottom: 12px;
    padding: 6px 10px;
  }

  .footer-section p,
  .footer-links a,
  .copyright,
  .stats {
    font-size: 12px;
  }

  .stats {
    gap: 8px;
  }
}
</style>
