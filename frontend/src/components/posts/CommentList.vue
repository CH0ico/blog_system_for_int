<template>
  <div class="comment-section">
    <div v-if="authStore.isAuthenticated" class="comment-editor">
      <el-input
        v-model="newContent"
        type="textarea"
        :rows="4"
        placeholder="写下你的想法，支持 Markdown 格式"
      />
      <div class="editor-actions">
        <div v-if="replyTarget" class="reply-tip">
          回复 @{{ replyTarget.author.nickname || replyTarget.author.username }}
          <el-button text size="small" @click="clearReply">取消</el-button>
        </div>
        <div class="actions-right">
          <el-button :disabled="submitting" @click="clearEditor"
            >清空</el-button
          >
          <el-button
            type="primary"
            :loading="submitting"
            @click="submitComment"
          >
            发布评论
          </el-button>
        </div>
      </div>
    </div>
    <el-alert
      v-else
      type="info"
      :closable="false"
      title="登录后即可发表评论"
      class="comment-login-alert"
    />

    <div v-if="loading" class="comment-loading">
      <el-skeleton :rows="3" animated />
    </div>
    <div v-else-if="comments.length" class="comment-list">
      <div v-for="item in comments" :key="item.id" class="comment-card">
        <div class="comment-meta">
          <el-avatar :size="36" :src="item.author.avatar">
            {{ item.author.nickname?.[0] || item.author.username[0] }}
          </el-avatar>
          <div class="meta-text">
            <div class="author">
              {{ item.author.nickname || item.author.username }}
            </div>
            <div class="time">{{ formatDate(item.created_at) }}</div>
          </div>
          <el-button text size="small" @click="setReplyTarget(item)"
            >回复</el-button
          >
        </div>
        <div class="comment-body" v-html="renderContent(item)"></div>

        <div v-if="item.replies?.length" class="reply-list">
          <div v-for="reply in item.replies" :key="reply.id" class="reply-card">
            <div class="comment-meta">
              <el-avatar :size="30" :src="reply.author.avatar">
                {{ reply.author.nickname?.[0] || reply.author.username[0] }}
              </el-avatar>
              <div class="meta-text">
                <div class="author">
                  {{ reply.author.nickname || reply.author.username }}
                </div>
                <div class="time">{{ formatDate(reply.created_at) }}</div>
              </div>
              <el-button
                text
                size="small"
                @click="setReplyTarget(reply, item.id)"
                >回复</el-button
              >
            </div>
            <div class="comment-body" v-html="renderContent(reply)"></div>
          </div>
        </div>
      </div>
    </div>
    <el-empty v-else description="还没有评论，快来抢沙发吧" />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import { ElMessage } from "element-plus";
import { marked } from "marked";
import hljs from "highlight.js";
import api from "@/utils/api";
import { useAuthStore } from "@/stores/auth";

const props = defineProps({
  postId: { type: Number, required: true },
  commentCount: { type: Number, default: 0 },
});
const emit = defineEmits(["update:commentCount", "posted"]);

const authStore = useAuthStore();
const comments = ref([]);
const loading = ref(false);
const submitting = ref(false);
const newContent = ref("");
const replyTarget = ref(null);
const replyParentId = ref(null);

marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
});

const renderContent = (comment) =>
  comment.content_html || marked.parse(comment.content || "");
const formatDate = (iso) => new Date(iso).toLocaleString("zh-CN");

const fetchComments = async () => {
  loading.value = true;
  try {
    const res = await api.get(`/posts/${props.postId}/comments`);
    comments.value = res.data.comments || [];
  } catch (error) {
    ElMessage.error("获取评论失败");
  } finally {
    loading.value = false;
  }
};

const clearEditor = () => {
  newContent.value = "";
  clearReply();
};

const clearReply = () => {
  replyTarget.value = null;
  replyParentId.value = null;
};

const setReplyTarget = (comment, parentId = null) => {
  replyTarget.value = comment;
  replyParentId.value = parentId || comment.parent_id || comment.id;
};

const submitComment = async () => {
  if (!newContent.value.trim()) {
    ElMessage.warning("请输入评论内容");
    return;
  }
  submitting.value = true;
  try {
    const payload = {
      content: newContent.value,
      parent_id: replyParentId.value,
    };
    const res = await api.post(`/posts/${props.postId}/comments`, payload);
    ElMessage.success("评论发布成功");
    newContent.value = "";
    clearReply();
    emit("update:commentCount", props.commentCount + 1);
    emit("posted", res.data.comment);
    fetchComments();
  } catch (error) {
    const msg = error.response?.data?.message || "评论失败";
    ElMessage.error(msg);
  } finally {
    submitting.value = false;
  }
};

onMounted(() => {
  fetchComments();
});

watch(
  () => props.postId,
  () => fetchComments(),
);
</script>

<style scoped>
.comment-section {
  margin-top: 16px;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
}
.comment-editor {
  margin-bottom: 16px;
}
.editor-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.reply-tip {
  font-size: 13px;
  color: var(--el-color-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}
.actions-right {
  display: flex;
  gap: 8px;
}
.comment-login-alert {
  margin-bottom: 16px;
}
.comment-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.comment-card,
.reply-card {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 12px;
  background: var(--el-bg-color);
}
.comment-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.meta-text {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.author {
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.comment-body {
  line-height: 1.6;
  color: var(--el-text-color-primary);
}
.comment-body :deep(pre) {
  background: #1e1e1e;
  color: #fff;
  padding: 12px;
  border-radius: 6px;
  overflow: auto;
}
.comment-body :deep(code) {
  font-family: SFMono-Regular, Consolas, Menlo, Monaco, monospace;
}
.reply-list {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.reply-card {
  background: var(--el-fill-color-light);
}
.comment-loading {
  padding: 12px 0;
}
</style>
