<template>
  <div class="cassette-profile-terminal">
    <div class="profile-container">
      <!-- 页面头部 -->
      <header class="profile-header">
        <div class="header-content">
          <h1>USER PROFILE</h1>
          <p>MANAGE YOUR ACCOUNT</p>
        </div>
      </header>

      <!-- 主要内容 -->
      <main v-loading="loading" class="profile-content">
        <!-- 个人信息卡片 -->
        <section class="profile-section">
          <div class="section-header">
            <span class="section-label">PERSONAL INFORMATION</span>
          </div>
          <div class="profile-grid">
            <!-- 头像卡片 -->
            <div class="profile-card avatar-card">
              <h3>AVATAR</h3>
              <div class="avatar-section">
                <el-upload
                  class="avatar-uploader"
                  :show-file-list="false"
                  action="/api/auth/avatar"
                  name="file"
                  :headers="uploadHeaders"
                  :on-success="handleAvatarSuccess"
                >
                  <div class="avatar-wrapper">
                    <img v-if="user.avatar" :src="user.avatar" class="avatar" />
                    <div v-else class="avatar-uploader-icon">
                      <span class="icon">+</span>
                      UPLOAD AVATAR
                    </div>
                  </div>
                </el-upload>
              </div>
            </div>

            <!-- 基本信息卡片 -->
            <div class="profile-card info-card">
              <h3>BASIC INFORMATION</h3>
              <div class="profile-form">
                <div class="form-group">
                  <label class="form-label">NICKNAME</label>
                  <el-input
                    v-model="form.nickname"
                    placeholder="ENTER YOUR NICKNAME"
                    class="profile-input"
                  />
                </div>

                <div class="form-group">
                  <label class="form-label">BIOGRAPHY</label>
                  <el-input
                    v-model="form.bio"
                    type="textarea"
                    placeholder="WRITE SOMETHING ABOUT YOURSELF"
                    class="profile-textarea"
                  />
                </div>

                <div class="form-group">
                  <label class="form-label">WEBSITE</label>
                  <el-input
                    v-model="form.website"
                    placeholder="https://example.com"
                    class="profile-input"
                  />
                  <p class="help-text">MUST START WITH HTTP:// OR HTTPS://</p>
                </div>

                <div class="form-group">
                  <label class="form-label">LOCATION</label>
                  <el-input
                    v-model="form.location"
                    placeholder="YOUR CITY"
                    class="profile-input"
                  />
                </div>

                <div class="form-actions">
                  <button
                    class="profile-btn primary"
                    :loading="saving"
                    @click="save"
                  >
                    <span class="btn-icon">💾</span>
                    SAVE CHANGES
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 我的文章卡片 -->
        <section class="profile-section">
          <div class="section-header">
            <span class="section-label">MY ARTICLES</span>
          </div>
          <div class="profile-card posts-card">
            <h3>ARTICLE MANAGEMENT</h3>
            <div class="posts-tabs">
              <div class="tab-container">
                <button
                  class="tab-btn"
                  :class="{ active: postTab === 'published' }"
                  @click="
                    postTab = 'published';
                    loadPosts();
                  "
                >
                  PUBLISHED
                </button>
                <button
                  class="tab-btn"
                  :class="{ active: postTab === 'draft' }"
                  @click="
                    postTab = 'draft';
                    loadPosts();
                  "
                >
                  DRAFTS
                </button>
              </div>
            </div>
            <div v-if="myPosts.length" class="posts-list">
              <PostItem v-for="p in myPosts" :key="p.id" :post="p" />
            </div>
            <div v-else class="empty-state">
              <div class="empty-icon">📄</div>
              <div class="empty-text">NO ARTICLES FOUND</div>
              <div class="empty-subtext">NO POSTS IN THIS STATUS</div>
            </div>
          </div>
        </section>
      </main>
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
.cassette-profile-terminal {
  background: #fff9ed;
  min-height: 100vh;
  background-image:
    linear-gradient(rgba(230, 126, 34, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(230, 126, 34, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
}

.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
}

/* 页面头部 */
.profile-header {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 3px 3px 0 #e67e22;
  padding: 24px;
  margin-bottom: 30px;
  text-align: center;
}

.profile-header h1 {
  font-size: 28px;
  font-weight: 900;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0 0 8px 0;
  font-family: "Courier New", monospace;
}

.profile-header p {
  font-size: 14px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0;
  font-family: "Courier New", monospace;
}

/* 主要内容 */
.profile-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 个人信息卡片 */
.profile-section {
  margin-bottom: 24px;
}

.section-header {
  background: #e67e22;
  color: white;
  padding: 8px 16px;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  display: inline-block;
  margin-bottom: 16px;
}

.section-label {
  font-family: "Courier New", monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 14px;
}

.profile-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 20px;
  align-items: start;
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}

/* 卡片样式 */
.profile-card {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  padding: 20px;
  transition: all 0.2s ease;
}

.profile-card:hover {
  box-shadow: 4px 4px 0 #e67e22;
  transform: translate(-2px, -2px);
}

.profile-card h3 {
  font-family: "Courier New", monospace;
  font-size: 16px;
  font-weight: 700;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin: 0 0 16px 0;
  border-bottom: 2px solid #e67e22;
  padding-bottom: 8px;
}

/* 头像部分 */
.avatar-card {
  text-align: center;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.avatar-uploader {
  width: 100%;
}

.avatar-wrapper {
  position: relative;
  width: 180px;
  height: 180px;
  margin: 0 auto;
}

.avatar {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #e67e22;
  object-fit: cover;
  transition: all 0.2s ease;
}

.avatar:hover {
  box-shadow: 4px 4px 0 #e67e22;
  transform: translate(-2px, -2px);
}

.avatar-uploader-icon {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px dashed #2c2c2c;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fff9ed;
}

.avatar-uploader-icon:hover {
  background: #fdebd0;
  border-color: #e67e22;
  transform: scale(1.02);
}

.avatar-uploader-icon .icon {
  font-size: 24px;
  color: #e67e22;
}

.avatar-uploader-icon span:last-child {
  font-family: "Courier New", monospace;
  font-size: 12px;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 表单样式 */
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-family: "Courier New", monospace;
  font-size: 13px;
  font-weight: 600;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.profile-input,
.profile-textarea {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  padding: 10px 12px;
  font-size: 14px;
  color: #2c2c2c;
  font-family: "Courier New", monospace;
  border-radius: 0;
  transition: all 0.2s ease;
}

.profile-input:focus,
.profile-textarea:focus {
  border-color: #e67e22;
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
}

.profile-textarea {
  resize: vertical;
  min-height: 100px;
}

.help-text {
  font-family: "Courier New", monospace;
  font-size: 12px;
  color: #666;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-start;
}

.profile-btn {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  padding: 10px 20px;
  font-size: 13px;
  color: #2c2c2c;
  cursor: pointer;
  transition: all 0.1s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  font-family: "Courier New", monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-radius: 0;
}

.profile-btn:hover {
  background: #f8f8f8;
  border-color: #e67e22;
  color: #e67e22;
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
}

.profile-btn.primary {
  background: #e67e22;
  border-color: #2c2c2c;
  color: white;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.profile-btn.primary:hover {
  background: #d35400;
  border-color: #2c2c2c;
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

/* 文章列表 */
.posts-card {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  padding: 20px;
}

.posts-tabs {
  margin-bottom: 16px;
}

.tab-container {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.tab-btn {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  padding: 8px 16px;
  font-size: 13px;
  color: #2c2c2c;
  cursor: pointer;
  transition: all 0.1s ease;
  font-family: "Courier New", monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-radius: 0;
}

.tab-btn:hover {
  background: #f8f8f8;
  border-color: #e67e22;
  color: #e67e22;
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
}

.tab-btn.active {
  background: #e67e22;
  color: white;
  box-shadow: 2px 2px 0 #2c2c2c;
}

.posts-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  background: #fff9ed;
  border: 2px dashed #2c2c2c;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-text {
  font-family: "Courier New", monospace;
  font-size: 16px;
  font-weight: 600;
  color: #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.empty-subtext {
  font-family: "Courier New", monospace;
  font-size: 13px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
</style>
