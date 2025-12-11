<template>
  <div class="little-helper" :style="stylePos">
    <button
      class="avatar bounce"
      @mousedown="onDown"
      @touchstart="onDown"
      @click="toggle"
    >
      <span class="emoji">🐱</span>
    </button>

    <el-dialog v-model="tipsVisible" title="小助手" width="380px">
      <div class="quick-actions">
        <el-button size="small" type="primary" @click="goWrite"
          >写文章</el-button
        >
        <el-button size="small" @click="goPosts">浏览文章</el-button>
        <el-button size="small" @click="goProfile">个人中心</el-button>
        <el-button
          size="small"
          type="success"
          :loading="testing"
          @click="speedTest"
          >网络测速</el-button
        >
      </div>
      <div class="tips">
        <p>拖动我到你喜欢的位置吧～</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "@/utils/api";

const router = useRouter();
const tipsVisible = ref(false);
const testing = ref(false);

const pos = ref({ x: 24, y: 24 });
const dragging = ref(false);
let start = { x: 0, y: 0 };

const stylePos = {
  right: `${pos.value.x}px`,
  bottom: `${pos.value.y}px`,
};

const updateStyle = () => {
  stylePos.right = `${pos.value.x}px`;
  stylePos.bottom = `${pos.value.y}px`;
};

const toggle = () => {
  tipsVisible.value = !tipsVisible.value;
};

const goWrite = () => router.push("/write");
const goPosts = () => router.push("/posts");
const goProfile = () => router.push("/profile");

const speedTest = async () => {
  if (testing.value) return;
  testing.value = true;
  const t0 = performance.now();
  try {
    await api.get("/posts", { params: { per_page: 1 } });
    const dt = Math.round(performance.now() - t0);
    ElMessage.success(`网络延迟约 ${dt} ms`);
  } catch (e) {
    ElMessage.error("网络测试失败");
  } finally {
    testing.value = false;
  }
};

const onMove = (e) => {
  if (!dragging.value) return;
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;
  const dx = start.x - clientX;
  const dy = start.y - clientY;
  pos.value.x = Math.max(
    12,
    Math.min(window.innerWidth - 60, pos.value.x + dx),
  );
  pos.value.y = Math.max(
    12,
    Math.min(window.innerHeight - 60, pos.value.y + dy),
  );
  start = { x: clientX, y: clientY };
  updateStyle();
};

const onUp = () => {
  dragging.value = false;
  try {
    localStorage.setItem("helper_pos", JSON.stringify(pos.value));
  } catch {}
  window.removeEventListener("mousemove", onMove);
  window.removeEventListener("mouseup", onUp);
  window.removeEventListener("touchmove", onMove);
  window.removeEventListener("touchend", onUp);
};

const onDown = (e) => {
  dragging.value = true;
  const clientX = e.touches ? e.touches[0].clientX : e.clientX;
  const clientY = e.touches ? e.touches[0].clientY : e.clientY;
  start = { x: clientX, y: clientY };
  window.addEventListener("mousemove", onMove);
  window.addEventListener("mouseup", onUp);
  window.addEventListener("touchmove", onMove);
  window.addEventListener("touchend", onUp);
};

onMounted(() => {
  try {
    const saved = JSON.parse(localStorage.getItem("helper_pos") || "{}");
    if (typeof saved.x === "number" && typeof saved.y === "number") {
      pos.value = saved;
      updateStyle();
    }
  } catch {}
});
</script>

<style scoped>
.little-helper {
  position: fixed;
  z-index: 1100;
}
.avatar {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  border: 2px solid var(--el-color-primary);
  background: var(--el-bg-color);
  box-shadow: var(--el-box-shadow);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: grab;
}
.emoji {
  font-size: 26px;
}
.bounce {
  animation: bounce 2s infinite;
}
@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}
.quick-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.tips {
  margin-top: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
