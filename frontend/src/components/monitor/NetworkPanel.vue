<template>
  <div class="network-panel">
    <div class="header">
      <h3>网络性能监测</h3>
      <el-button size="small" :loading="testing" @click="runTest"
        >立即测试</el-button
      >
    </div>
    <div class="metrics">
      <div class="metric">
        <div class="label">平均延迟</div>
        <div class="value">{{ avgLatency }} ms</div>
      </div>
      <div class="metric">
        <div class="label">平均吞吐</div>
        <div class="value">{{ avgThroughput }} KB/s</div>
      </div>
      <div class="metric">
        <div class="label">成功率</div>
        <div class="value">{{ successRate }}%</div>
      </div>
      <div class="metric">
        <div class="label">采样数</div>
        <div class="value">{{ samples.length }}</div>
      </div>
    </div>

    <div v-if="samples.length" class="samples">
      <div v-for="(s, i) in samples.slice(-5)" :key="i" class="sample">
        <span>延迟: {{ s.latency }} ms</span>
        <span>吞吐: {{ s.throughput }} KB/s</span>
        <span :class="{ ok: s.ok, fail: !s.ok }">{{
          s.ok ? "成功" : "失败"
        }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import api from "@/utils/api";

const samples = ref([]);
const testing = ref(false);
let timer = null;

const avgLatency = computed(() => {
  const arr = samples.value;
  if (!arr.length) return 0;
  return Math.round(arr.reduce((sum, s) => sum + s.latency, 0) / arr.length);
});

const avgThroughput = computed(() => {
  const arr = samples.value;
  if (!arr.length) return 0;
  return Math.round(arr.reduce((sum, s) => sum + s.throughput, 0) / arr.length);
});

const successRate = computed(() => {
  const arr = samples.value;
  if (!arr.length) return 100;
  const ok = arr.filter((s) => s.ok).length;
  return Math.round((ok / arr.length) * 100);
});

const measure = async () => {
  const start = performance.now();
  let ok = true;
  let sizeKB = 0;
  try {
    // 请求一个轻量接口，默认获取文章列表第一页
    const res = await api.get("/posts", { params: { per_page: 1 } });
    const end = performance.now();
    const latency = Math.max(1, Math.round(end - start));
    // 计算响应大小：优先从content-length，否则用JSON长度估算
    const len = Number(res.headers["content-length"]) || 0;
    if (len > 0) {
      sizeKB = Math.round(len / 1024);
    } else {
      const payloadStr = JSON.stringify(res.data || {});
      sizeKB = Math.max(1, Math.round(payloadStr.length / 1024));
    }
    // 吞吐 = 大小KB / 秒
    const seconds = latency / 1000;
    const throughput = Math.max(1, Math.round(sizeKB / (seconds || 0.001)));
    samples.value.push({ latency, throughput, ok });
  } catch (e) {
    ok = false;
    const end = performance.now();
    const latency = Math.max(1, Math.round(end - start));
    samples.value.push({ latency, throughput: 0, ok });
  }
  // 限制样本数量
  if (samples.value.length > 50) samples.value.shift();
};

const runTest = async () => {
  if (testing.value) return;
  testing.value = true;
  try {
    await measure();
  } finally {
    testing.value = false;
  }
};

onMounted(() => {
  // 周期性采样
  timer = setInterval(measure, 10000);
  // 初始采样
  measure();
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style scoped>
.network-panel {
  background: var(--el-bg-color);
  border: 2px solid var(--el-color-primary);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--el-box-shadow);
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.metric {
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 10px;
  padding: 10px;
}
.label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
.value {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.samples {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.sample {
  display: flex;
  gap: 16px;
  font-size: 13px;
}
.ok {
  color: var(--el-color-success);
}
.fail {
  color: var(--el-color-danger);
}
</style>
