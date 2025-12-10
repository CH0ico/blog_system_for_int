<template>
  <div v-loading="loading" class="profile-page">
    <div class="container">
      <h1>个人中心</h1>
      <div class="grid">
        <div class="card">
          <h3>头像</h3>
          <el-upload
            class="avatar-uploader"
            :show-file-list="false"
            action="/api/auth/avatar"
            name="file"
            :headers="uploadHeaders"
            :on-success="handleAvatarSuccess"
          >
            <img v-if="user.avatar" :src="user.avatar" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </div>

        <div class="card">
          <h3>基本信息</h3>
          <el-form :model="form" label-width="80px">
            <el-form-item label="昵称">
              <el-input v-model="form.nickname" />
            </el-form-item>
            <el-form-item label="签名">
              <el-input v-model="form.bio" type="textarea" />
            </el-form-item>
            <el-form-item label="网站">
              <el-input
                v-model="form.website"
                placeholder="https://example.com"
              />
              <p class="help">需要以 http:// 或 https:// 开头</p>
            </el-form-item>
            <el-form-item label="城市">
              <el-input v-model="form.location" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="saving" @click="save"
                >保存</el-button
              >
            </el-form-item>
          </el-form>
        </div>

        <div class="card">
          <h3>我的文章</h3>
          <el-tabs v-model="postTab" @tab-change="loadPosts">
            <el-tab-pane label="已发布" name="published" />
            <el-tab-pane label="草稿" name="draft" />
          </el-tabs>
          <div v-if="myPosts.length" class="posts">
            <PostItem v-for="p in myPosts" :key="p.id" :post="p" />
          </div>
          <el-empty v-else description="暂无该状态的文章" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from "vue";
import { Plus } from "@element-plus/icons-vue";
import { useAuthStore } from "@/stores/auth";
import { usePostsStore } from "@/stores/posts";
import { ElMessage } from "element-plus";
import PostItem from "@/components/posts/PostItem.vue";

const authStore = useAuthStore();
const postsStore = usePostsStore();
const loading = ref(false);
const saving = ref(false);
const user = computed(() => authStore.user || {});
const form = reactive({ nickname: "", bio: "", website: "", location: "" });
const postTab = ref("published");
const myPosts = ref([]);

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.accessToken}`,
}));

const load = async () => {
  loading.value = true;
  await authStore.fetchUser();
  form.nickname = user.value.nickname || "";
  form.bio = user.value.bio || "";
  form.website = user.value.website || "";
  form.location = user.value.location || "";
  await loadPosts();
  loading.value = false;
};

const loadPosts = async () => {
  const status = postTab.value === "draft" ? "draft" : "published";
  const res = await postsStore.fetchPosts({ status, per_page: 20, mine: true });
  myPosts.value = res.posts || postsStore.posts;
};

const save = async () => {
  saving.value = true;
  try {
    await authStore.updateProfile({ ...form });
    ElMessage.success("更新成功");
  } catch (e) {
    /* handled by store */
  } finally {
    saving.value = false;
  }
};

const handleAvatarSuccess = (res) => {
  if (res.avatar) {
    authStore.user.avatar = res.avatar;
    ElMessage.success("头像已更新");
  }
};

onMounted(load);
</script>

<style scoped>
.profile-page {
  padding: 24px 0;
  background: var(--el-bg-color-page);
  min-height: 100vh;
}
.container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 20px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}
.card {
  background: #fff;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 16px;
}
.avatar-uploader {
  display: inline-block;
}
.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: block;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: var(--el-text-color-secondary);
  width: 120px;
  height: 120px;
  border: 1px dashed var(--el-border-color);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.help {
  margin: 4px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.posts {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}
</style>
