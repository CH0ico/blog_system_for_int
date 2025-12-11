<template>
  <div class="cassette-auth-terminal">
    <!-- CRT 屏幕特效 -->
    <div class="crt-overlay">
      <div class="scanlines"></div>
      <div class="noise"></div>
    </div>

    <div class="auth-console">
      <div class="console-header">
        <h1 class="console-title">AUTHENTICATION TERMINAL</h1>
        <p class="console-subtitle">SYSTEM ACCESS PROTOCOL</p>
      </div>

      <div class="console-form">
        <div class="form-group">
          <label class="form-label">USERNAME / EMAIL</label>
          <input
            v-model="loginForm.username_or_email"
            type="text"
            class="form-input"
            placeholder="ENTER USER CREDENTIALS"
            @keyup.enter="handleLogin"
          />
        </div>

        <div class="form-group">
          <label class="form-label">ACCESS CODE</label>
          <input
            v-model="loginForm.password"
            type="password"
            class="form-input"
            placeholder="ENTER SECURITY CODE"
            @keyup.enter="handleLogin"
          />
        </div>

        <div class="form-options">
          <label class="checkbox-container">
            <input
              v-model="loginForm.remember"
              type="checkbox"
              class="form-checkbox"
            />
            <span class="checkbox-label">REMEMBER SESSION</span>
          </label>
          <router-link to="/forgot-password" class="console-link">
            ACCESS RECOVERY
          </router-link>
        </div>

        <button class="console-btn" :disabled="loading" @click="handleLogin">
          <span v-if="!loading">EXECUTE LOGIN</span>
          <span v-else>PROCESSING...</span>
        </button>
      </div>

      <div class="console-footer">
        <p>
          NO SYSTEM ACCOUNT?
          <router-link to="/register" class="console-link"
            >INITIATE REGISTRATION</router-link
          >
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const loading = ref(false);

const loginForm = reactive({
  username_or_email: "",
  password: "",
  remember: false,
});

// 模拟机械音效
const playMechanicalSound = () => {
  // 创建机械按键音效
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const oscillator = audioContext.createOscillator();
  const gainNode = audioContext.createGain();

  oscillator.connect(gainNode);
  gainNode.connect(audioContext.destination);

  oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
  oscillator.frequency.exponentialRampToValueAtTime(
    400,
    audioContext.currentTime + 0.1,
  );

  gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
  gainNode.gain.exponentialRampToValueAtTime(
    0.01,
    audioContext.currentTime + 0.1,
  );

  oscillator.start(audioContext.currentTime);
  oscillator.stop(audioContext.currentTime + 0.1);
};

// 添加按钮点击音效
const addClickSound = () => {
  const buttons = document.querySelectorAll(".console-btn, .console-link");
  buttons.forEach((button) => {
    button.addEventListener("click", playMechanicalSound);
  });
};

// 组件挂载完成后添加音效
onMounted(() => {
  addClickSound();
});

const handleLogin = async () => {
  // 基础验证
  if (!loginForm.username_or_email.trim()) {
    alert("USERNAME/EMAIL REQUIRED");
    return;
  }
  if (!loginForm.password.trim()) {
    alert("ACCESS CODE REQUIRED");
    return;
  }
  if (loginForm.password.length < 6) {
    alert("ACCESS CODE MINIMUM 6 CHARACTERS");
    return;
  }

  try {
    loading.value = true;

    await authStore.login(loginForm);

    alert("AUTHENTICATION SUCCESSFUL");

    // 重定向到之前访问的页面或首页
    const redirect = route.query.redirect || "/";
    router.push(redirect);

    // 添加机械音效模拟
    playMechanicalSound();
  } catch (error) {
    alert(error.message || "AUTHENTICATION FAILED - CHECK CREDENTIALS");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.cassette-auth-terminal {
  position: relative;
  min-height: 100vh;
  background-color: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  animation: terminalBoot 0.5s ease-out;
}

@keyframes terminalBoot {
  0% {
    opacity: 0;
    transform: scale(0.9) translateY(20px);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.02) translateY(-5px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

/* CRT 屏幕特效 */
.crt-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.scanlines {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    0deg,
    rgba(21, 21, 21, 0.1) 0px,
    rgba(21, 21, 21, 0.1) 1px,
    transparent 1px,
    transparent 2px
  );
  animation: scanlines 8s linear infinite;
}

.noise {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
  animation: noise 0.5s steps(10) infinite;
}

@keyframes scanlines {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(10px);
  }
}

@keyframes noise {
  0%,
  100% {
    transform: translate(0, 0);
  }
  10% {
    transform: translate(-5%, -5%);
  }
  20% {
    transform: translate(-10%, 5%);
  }
  30% {
    transform: translate(5%, -10%);
  }
  40% {
    transform: translate(-5%, 15%);
  }
  50% {
    transform: translate(-10%, 5%);
  }
  60% {
    transform: translate(15%, 0);
  }
  70% {
    transform: translate(0, 10%);
  }
  80% {
    transform: translate(-15%, 0);
  }
  90% {
    transform: translate(10%, 5%);
  }
}

.auth-console {
  position: relative;
  z-index: 2;
  background: var(--color-eggshell);
  border: 4px solid var(--color-dark-black);
  box-shadow: 6px 6px 0 var(--color-dark-black);
  padding: 40px;
  max-width: 400px;
  width: 90%;
}

.console-header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 2px solid var(--color-dark-black);
  padding-bottom: 20px;
}

.console-title {
  margin: 0 0 10px 0;
  font-size: 1.5rem;
  font-weight: 900;
  color: var(--color-dark-black);
  letter-spacing: 2px;
  text-shadow: 3px 3px 0 var(--color-warning-orange);
}

.console-subtitle {
  margin: 0;
  font-size: 12px;
  color: var(--color-dark-black);
  opacity: 0.7;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.console-form {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 900;
  color: var(--color-dark-black);
  letter-spacing: 1px;
  text-transform: uppercase;
}

.form-input {
  width: 100%;
  padding: 12px 15px;
  border: 3px solid var(--color-dark-black);
  background: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  font-size: 14px;
  font-weight: 600;
  outline: none;
  transition: all 0.1s ease;
  box-shadow: 2px 2px 0 var(--color-dark-black);
}

.form-input:focus {
  box-shadow: 4px 4px 0 var(--color-dark-black);
  transform: translate(-2px, -2px);
  background: rgba(255, 107, 0, 0.1);
  animation: inputFocus 0.3s ease-out;
}

@keyframes inputFocus {
  0% {
    box-shadow: 2px 2px 0 var(--color-dark-black);
    transform: translate(0, 0);
  }
  50% {
    box-shadow: 6px 6px 0 var(--color-dark-black);
    transform: translate(-4px, -4px);
  }
  100% {
    box-shadow: 4px 4px 0 var(--color-dark-black);
    transform: translate(-2px, -2px);
  }
}

.form-input::placeholder {
  color: var(--color-dark-black);
  opacity: 0.5;
  font-weight: 400;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  flex-wrap: wrap;
  gap: 10px;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-checkbox {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-dark-black);
  appearance: none;
  background: var(--color-eggshell);
  cursor: pointer;
  position: relative;
}

.form-checkbox:checked {
  background: var(--color-warning-orange);
}

.form-checkbox:checked::after {
  content: "✓";
  position: absolute;
  top: -2px;
  left: 2px;
  font-size: 12px;
  font-weight: 900;
  color: var(--color-dark-black);
}

.checkbox-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-dark-black);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.console-link {
  color: var(--color-dark-black);
  text-decoration: none;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border-bottom: 2px solid var(--color-warning-orange);
  transition: all 0.1s ease;
}

.console-link:hover {
  color: var(--color-warning-orange);
  border-bottom-color: var(--color-dark-black);
}

.console-btn {
  width: 100%;
  padding: 15px 20px;
  border: 3px solid var(--color-dark-black);
  background: var(--color-eggshell);
  color: var(--color-dark-black);
  font-family: "Courier New", monospace;
  font-size: 14px;
  font-weight: 900;
  letter-spacing: 1px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.1s ease;
  box-shadow: 3px 3px 0 var(--color-dark-black);
}

.console-btn:hover {
  box-shadow: 5px 5px 0 var(--color-dark-black);
  transform: translate(-2px, -2px);
  background: var(--color-warning-orange);
  animation: buttonClick 0.2s ease-out;
}

@keyframes buttonClick {
  0% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-2px, -2px) scale(0.95);
  }
  100% {
    transform: translate(-2px, -2px) scale(1);
  }
}

/* 响应式布局优化 */
@media (max-width: 768px) {
  .auth-console {
    padding: 30px 20px;
    max-width: 90%;
  }

  .console-title {
    font-size: 1.2rem;
  }

  .console-form {
    margin-bottom: 20px;
  }

  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .console-footer {
    text-align: center;
  }
}

@media (max-width: 480px) {
  .auth-console {
    padding: 20px 15px;
    border-width: 2px;
    box-shadow: 3px 3px 0 var(--color-dark-black);
  }

  .console-title {
    font-size: 1rem;
    letter-spacing: 1px;
  }

  .form-input {
    padding: 10px 12px;
    font-size: 13px;
    border-width: 2px;
    box-shadow: 1px 1px 0 var(--color-dark-black);
  }

  .console-btn {
    padding: 12px 15px;
    font-size: 13px;
    border-width: 2px;
    box-shadow: 2px 2px 0 var(--color-dark-black);
  }

  .form-label {
    font-size: 11px;
  }

  .checkbox-label,
  .console-link {
    font-size: 11px;
  }
}

.console-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  box-shadow: 3px 3px 0 var(--color-dark-black);
}

.console-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 2px solid var(--color-dark-black);
  color: var(--color-dark-black);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.console-footer p {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .auth-console {
    padding: 30px 20px;
  }

  .console-title {
    font-size: 1.2rem;
  }

  .form-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .console-btn {
    padding: 12px 15px;
    font-size: 12px;
  }
}
</style>
