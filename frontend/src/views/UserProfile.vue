<template>
  <div v-loading="loading" class="user-profile">
    <div v-if="user" class="container">
      <div class="header">
        <el-avatar :size="80" :src="user.avatar">
          {{ user.nickname?.[0] || user.username?.[0] }}
        </el-avatar>
        <div class="meta">
          <h2>{{ user.nickname || user.username }}</h2>
          <p v-if="user.bio">{{ user.bio }}</p>
          <div class="stats">
            <span>粉丝 {{ user.followers_count }}</span>
            <span>关注 {{ user.following_count }}</span>
            <span>文章 {{ user.posts_count }}</span>
          </div>
        </div>
        <div
          v-if="authStore.isAuthenticated && authStore.user.id !== user.id"
          class="actions"
        >
          <el-button type="primary" :loading="following" @click="toggleFollow">
            {{ user.is_following ? "取消关注" : "关注TA" }}
          </el-button>
        </div>
      </div>

      <div v-if="posts.length" class="posts">
        <h3>TA 的文章</h3>
        <PostItem v-for="p in posts" :key="p.id" :post="p" />
      </div>
      <el-empty v-else description="暂无文章" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import PostItem from "@/components/posts/PostItem.vue";
import { useAuthStore } from "@/stores/auth";
import { usePostsStore } from "@/stores/posts";
import { ElMessage } from "element-plus";
import api from "@/utils/api";

const route = useRoute();
const authStore = useAuthStore();
const postsStore = usePostsStore();
const loading = ref(false);
const following = ref(false);
const user = ref(null);
const posts = computed(() => postsStore.posts);

const loadUser = async () => {
  const res = await api.get(`/auth/user/${route.params.username}`);
  user.value = res.data.user;
};

const loadPosts = async () => {
  await postsStore.fetchPosts({ author: route.params.username, per_page: 20 });
};

const toggleFollow = async () => {
  if (!authStore.isAuthenticated) {
    ElMessage.warning("请先登录");
    return;
  }
  following.value = true;
  try {
    const res = await api.post(`/users/${user.value.id}/follow`);
    user.value.is_following = res.data.following;
    user.value.followers_count = res.data.followers_count;
  } catch (e) {
    ElMessage.error("操作失败");
  } finally {
    following.value = false;
  }
};

onMounted(async () => {
  loading.value = true;
  try {
    await loadUser();
    await loadPosts();
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.user-profile {
  padding: 24px 0;
  background: var(--el-bg-color-page);
  min-height: 100vh;
}
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}
.header {
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  gap: 16px;
  align-items: center;
}
.meta h2 {
  margin: 0 0 4px 0;
}
.meta p {
  margin: 0;
  color: var(--el-text-color-secondary);
}
.stats {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-top: 6px;
}
.actions {
  margin-left: auto;
}
.posts {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
