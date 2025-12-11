<template>
  <div class="cassette-terminal">
    <!-- CRT 屏幕特效层 -->
    <div class="crt-overlay">
      <div class="scanlines"></div>
      <div class="noise"></div>
    </div>

    <div class="not-found-container">
      <!-- 顶部装饰栏 -->
      <div class="top-bar-deco">
        <span class="tag-black">ERROR: 404</span>
        <div class="line-fill"></div>
        <span class="rec-date">REC_DATE: {{ currentDate }}</span>
      </div>

      <!-- 主要内容 -->
      <main class="not-found-content">
        <!-- 错误标题 -->
        <header class="error-header">
          <h1 class="glitch-text" data-text="ERROR: 404">ERROR: 404</h1>
          <h2 class="error-subtitle">FILE NOT FOUND</h2>
        </header>

        <!-- 警告区域 -->
        <section class="warning-section">
          <div class="hazard-stripe"></div>
          <div class="warning-content">
            <div class="warning-text">
              <h3>MISSION FAILED</h3>
              <p>THE REQUESTED RESOURCE COULD NOT BE LOCATED. THIS INCIDENT WILL BE REPORTED.</p>
            </div>
          </div>
        </section>

        <!-- 错误详情 -->
        <section class="error-details">
          <div class="entity-grid">
            <div class="entity-card">
              <div class="card-head">
                <span>ERROR CODE</span>
                <span class="badge-black">404</span>
              </div>
              <div class="card-body">
                <p>RESOURCE NOT FOUND</p>
                <div class="stat-big">FILE_MISSING</div>
              </div>
            </div>

            <div class="entity-card">
              <div class="card-head">
                <span>RECOMMENDED ACTION</span>
                <span class="badge-black">NAVIGATE</span>
              </div>
              <div class="card-body">
                <button class="industrial-btn" @click="$router.push('/')">
                  [ RETURN_TO_MAINFRAME ]
                </button>
                <button class="industrial-btn" @click="$router.push('/posts')">
                  [ ACCESS_ARCHIVES ]
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

// 获取当前日期
const currentDate = ref('');

onMounted(() => {
  const now = new Date();
  currentDate.value = now.toISOString().split('T')[0];
});
</script>

<style scoped>
.cassette-terminal {
  background-color: #fff9ed;
  color: #2c2c2c;
  font-family: 'Courier New', monospace;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
  border: 10px solid #2c2c2c;
  box-sizing: border-box;
}

/* CRT 特效 */
.crt-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.6;
  mix-blend-mode: overlay;
}

.scanlines {
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to bottom,
    rgba(255, 255, 255, 0),
    rgba(255, 255, 255, 0) 50%,
    rgba(0, 0, 0, 0.15) 50%,
    rgba(0, 0, 0, 0.15)
  );
  background-size: 100% 4px;
  animation: scanline-move 0.1s linear infinite;
}

@keyframes scanline-move {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(4px);
  }
}

.noise {
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.05);
  animation: noise-flicker 0.2s infinite alternate;
}

@keyframes noise-flicker {
  0% {
    opacity: 0.08;
  }
  100% {
    opacity: 0.12;
  }
}

/* 主容器 */
.not-found-container {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

/* 顶部装饰栏 */
.top-bar-deco {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px 20px;
  background: #fff;
  border-bottom: 2px solid #2c2c2c;
  box-shadow: 0 2px 0 #e67e22;
}

.tag-black {
  background: #2c2c2c;
  color: #fff;
  padding: 4px 10px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.line-fill {
  height: 2px;
  background: #2c2c2c;
  flex-grow: 1;
  margin: 0 10px;
}

.rec-date {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 主要内容区域 */
.not-found-content {
  flex-grow: 1;
  background-image: 
    linear-gradient(rgba(230, 126, 34, 0.1) 1px, transparent 1px),
    linear-gradient(90deg, rgba(230, 126, 34, 0.1) 1px, transparent 1px);
  background-size: 20px 20px;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

/* 错误标题 */
.error-header {
  text-align: center;
  margin-bottom: 40px;
}

.error-header h1 {
  font-size: clamp(4rem, 12vw, 10rem);
  font-weight: 900;
  color: #e67e22;
  text-transform: uppercase;
  margin: 0;
  text-shadow: 
    4px 4px 0 #2c2c2c,
    -2px -2px 0 #2c2c2c,
    2px -2px 0 #2c2c2c,
    -2px 2px 0 #2c2c2c,
    2px 2px 0 #2c2c2c;
  animation: glitch 2s infinite;
}

@keyframes glitch {
  0%, 90%, 100% {
    transform: translate(0);
  }
  92% {
    transform: translate(-5px, 5px);
  }
  94% {
    transform: translate(5px, -5px);
  }
  96% {
    transform: translate(-5px, -5px);
  }
  98% {
    transform: translate(5px, 5px);
  }
}

.error-subtitle {
  font-size: clamp(1.5rem, 4vw, 3rem);
  font-weight: 700;
  color: #2c2c2c;
  text-transform: uppercase;
  margin: 0;
  letter-spacing: 3px;
  background: #fff;
  padding: 10px 20px;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  display: inline-block;
}

/* 警告区域 */
.warning-section {
  background: #fff;
  border: 2px solid #2c2c2c;
  box-shadow: 0 4px 0 #e67e22;
  margin-bottom: 30px;
  width: 100%;
  max-width: 800px;
}

.hazard-stripe {
  background: linear-gradient(45deg, #e67e22 25%, transparent 25%, transparent 50%, #e67e22 50%, #e67e22 75%, transparent 75%, transparent);
  background-size: 20px 20px;
  height: 10px;
  border-bottom: 2px solid #2c2c2c;
}

.warning-content {
  padding: 20px;
}

.warning-text h3 {
  font-size: 1.5rem;
  font-weight: 900;
  color: #2c2c2c;
  text-transform: uppercase;
  margin: 0 0 15px 0;
  letter-spacing: 2px;
}

.warning-text p {
  font-size: 1rem;
  color: #2c2c2c;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 1px;
  line-height: 1.5;
}

/* 错误详情 */
.error-details {
  width: 100%;
  max-width: 800px;
}

.entity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.entity-card {
  background: #fff;
  border: 2px solid #2c2c2c;
  box-shadow: 3px 3px 0 #e67e22;
  padding: 20px;
  transition: all 0.2s ease;
}

.entity-card:hover {
  box-shadow: 5px 5px 0 #e67e22;
  transform: translate(-2px, -2px);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e67e22;
}

.card-head span:first-child {
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #2c2c2c;
}

.badge-black {
  background: #2c2c2c;
  color: #fff;
  padding: 2px 8px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.card-body p {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-big {
  font-size: 1.8rem;
  font-weight: 900;
  color: #e67e22;
  text-transform: uppercase;
  letter-spacing: 2px;
}

/* 按钮样式 */
.industrial-btn {
  background: #fff;
  border: 2px solid #2c2c2c;
  box-shadow: 3px 3px 0 #e67e22;
  padding: 12px 20px;
  font-size: 0.9rem;
  color: #2c2c2c;
  cursor: pointer;
  transition: all 0.1s ease;
  font-family: 'Courier New', monospace;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  text-align: center;
  margin: 5px 0;
}

.industrial-btn:hover {
  background: #f8f8f8;
  border-color: #e67e22;
  color: #e67e22;
  box-shadow: 5px 5px 0 #2c2c2c;
  transform: translate(-2px, -2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .top-bar-deco {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .line-fill {
    width: 100%;
    margin: 10px 0;
  }

  .entity-grid {
    grid-template-columns: 1fr;
  }

  .error-header h1 {
    font-size: 3rem;
  }

  .error-subtitle {
    font-size: 1.5rem;
  }
}
</style>