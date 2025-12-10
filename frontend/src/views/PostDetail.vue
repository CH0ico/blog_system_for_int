<!-- PostDetail.vue -->
<template>
  <div v-loading="loading" class="post-detail">
    <!-- 文章头部 -->
    <header v-if="post" class="post-header">
      <div class="container">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/posts' }">文章</el-breadcrumb-item>
          <el-breadcrumb-item>{{ post.title }}</el-breadcrumb-item>
        </el-breadcrumb>

        <h1 class="post-title">{{ post.title }}</h1>

        <div class="post-meta">
          <div class="meta-left">
            <el-avatar :src="post.author.avatar" :size="40">
              {{ post.author.nickname?.[0] || post.author.username[0] }}
            </el-avatar>
            <div class="author-info">
              <router-link
                :to="`/users/${post.author.username}`"
                class="author-name"
              >
                {{ post.author.nickname || post.author.username }}
              </router-link>
              <div class="post-time">
                <el-icon><Clock /></el-icon>
                <span>{{
                  formatDate(post.published_at || post.created_at)
                }}</span>
                ·
                <span>{{ post.view_count }} 次阅读</span>
              </div>
            </div>
          </div>

          <div class="meta-right">
            <el-tag
              v-for="tag in post.tags"
              :key="tag.id"
              type="info"
              size="small"
              @click="$router.push(`/tags/${tag.slug}`)"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
      </div>
    </header>

    <!-- 文章内容 -->
    <main v-if="post" class="post-body">
      <div class="container">
        <div class="post-content-wrapper">
          <!-- 文章摘要 -->
          <div v-if="post.summary" class="post-summary">
            <el-alert :title="post.summary" type="info" :closable="false" />
          </div>

          <!-- 正文 -->
          <article
            class="post-content article-content"
            v-html="postContentHtml"
          ></article>

          <!-- 分类 -->
          <div v-if="post.categories.length" class="post-categories">
            <el-icon><Folder /></el-icon>
            <span
              v-for="cat in post.categories"
              :key="cat.id"
              @click="$router.push(`/categories/${cat.slug}`)"
            >
              {{ cat.name }}
            </span>
          </div>

          <!-- 版权声明 -->
          <div class="post-license">
            <el-alert title="版权声明" type="warning" :closable="false">
              <template #default>
                本文采用
                <el-link
                  href="https://creativecommons.org/licenses/by-nc-sa/4.0/"
                  target="_blank"
                  type="primary"
                >
                  CC BY-NC-SA 4.0
                </el-link>
                协议，转载请注明出处。
              </template>
            </el-alert>
          </div>
        </div>
      </div>
    </main>

    <!-- 互动栏 -->
    <section v-if="post" class="post-actions">
      <div class="container">
        <div class="action-buttons">
          <el-button
            :type="post.liked ? 'primary' : 'default'"
            circle
            @click="toggleLike"
          >
            <el-icon><Pointer /></el-icon>
          </el-button>
          <span class="action-count">{{ post.like_count }}</span>

          <el-button
            :type="post.favorited ? 'warning' : 'default'"
            circle
            @click="toggleFavorite"
          >
            <el-icon><Star /></el-icon>
          </el-button>
          <span class="action-count">{{ post.favorite_count }}</span>

          <el-button circle @click="copyLink">
            <el-icon><Link /></el-icon>
          </el-button>

          <el-dropdown trigger="click" @command="handleMoreAction">
            <el-button circle>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="report">举报</el-dropdown-item>
                <el-dropdown-item v-if="canEdit" command="edit" divided>
                  编辑
                </el-dropdown-item>
                <el-dropdown-item
                  v-if="canEdit"
                  command="delete"
                  style="color: var(--el-color-danger)"
                >
                  删除
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </section>

    <!-- 评论区 -->
    <section v-if="post && post.allow_comments" class="post-comments">
      <div class="container">
        <h3>评论</h3>
        <CommentList
          v-model:comment-count="post.comment_count"
          :post-id="post.id"
          @posted="post.comment_count += 1"
        />
      </div>
    </section>

    <!-- 404 / 无权限 -->
    <div v-else-if="!loading" class="error-state">
      <el-result
        icon="warning"
        title="文章不存在或无权限查看"
        sub-title="请检查链接是否正确，或登录后重试"
      >
        <template #extra>
          <el-button type="primary" @click="$router.push('/posts')">
            返回文章列表
          </el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Clock,
  Pointer,
  Star,
  Link,
  MoreFilled,
  Folder,
} from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import { usePostsStore } from "@/stores/posts";
import { marked } from "marked";
import hljs from "highlight.js";
import CommentList from "@/components/posts/CommentList.vue";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const postsStore = usePostsStore();

const loading = ref(true);
const post = ref(null);

const canEdit = computed(
  () =>
    authStore.isAuthenticated &&
    post.value &&
    (post.value.author.id === authStore.user.id || authStore.user.is_admin),
);

marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
});

const renderMarkdown = (raw) => marked.parse(raw || "");
const postContentHtml = computed(
  () => post.value?.content_html || renderMarkdown(post.value?.content || ""),
);

const formatDate = (iso) => {
  const date = new Date(iso);
  return date.toLocaleString("zh-CN");
};

const fetchPost = async () => {
  loading.value = true;
  try {
    const res = await fetch(`/api/posts/${route.params.id}`, {
      headers: authStore.token
        ? { Authorization: `Bearer ${authStore.token}` }
        : {},
    });
    if (!res.ok) throw new Error("fetch error");
    const data = await res.json();
    post.value = data.post;
  } catch (e) {
    post.value = null;
  } finally {
    loading.value = false;
  }
};

const toggleLike = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning("请先登录");
    return;
  }
  await postsStore.toggleLike(post.value.id);
  post.value.liked = !post.value.liked;
  post.value.like_count += post.value.liked ? 1 : -1;
};

const toggleFavorite = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning("请先登录");
    return;
  }
  await postsStore.toggleFavorite(post.value.id);
  post.value.favorited = !post.value.favorited;
  post.value.favorite_count += post.value.favorited ? 1 : -1;
};

const copyLink = () => {
  navigator.clipboard.writeText(location.href);
  ElMessage.success("链接已复制");
};

const handleMoreAction = (cmd) => {
  switch (cmd) {
    case "edit":
      router.push(`/write?id=${post.value.id}`);
      break;
    case "delete":
      ElMessageBox.confirm("确定删除该文章吗？", "提示", { type: "warning" })
        .then(async () => {
          await postsStore.deletePost(post.value.id);
          ElMessage.success("删除成功");
          router.replace("/posts");
        })
        .catch(() => {});
      break;
    case "report":
      ElMessage.info("举报功能开发中");
      break;
  }
};

onMounted(() => {
  fetchPost();
});
</script>

<style scoped>
.post-detail {
  background: var(--el-bg-color-page);
  min-height: 100vh;
}
.container {
  max-width: 860px;
  margin: 0 auto;
  padding: 0 20px;
}
.post-header {
  background: #fff;
  padding: 24px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.post-title {
  font-size: 2rem;
  margin: 16px 0;
  line-height: 1.4;
}
.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.meta-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.author-info {
  display: flex;
  flex-direction: column;
}
.author-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
  text-decoration: none;
}
.post-time {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}
.meta-right {
  display: flex;
  gap: 8px;
}
.post-body {
  padding: 32px 0;
}
.post-summary {
  margin-bottom: 24px;
}
.post-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--el-text-color-primary);
}
.post-categories {
  margin-top: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
.post-categories span {
  cursor: pointer;
  color: var(--el-color-primary);
}
.post-license {
  margin-top: 32px;
}
.post-actions {
  background: #fff;
  padding: 16px 0;
  border-top: 1px solid var(--el-border-color-lighter);
  position: sticky;
  bottom: 0;
}
.action-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}
.action-count {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-right: 16px;
}
.post-comments {
  background: #fff;
  margin-top: 24px;
  padding: 32px 0;
}
.placeholder {
  text-align: center;
  color: var(--el-text-color-secondary);
}
.error-state {
  padding: 80px 20px;
  display: flex;
  justify-content: center;
}
@media (max-width: 768px) {
  .post-title {
    font-size: 1.5rem;
  }
  .post-meta {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
