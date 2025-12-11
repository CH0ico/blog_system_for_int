<template>
  <div class="cassette-auth-terminal">
    <!-- CRT 屏幕特效 -->
    <div class="crt-overlay">
      <div class="scanlines"></div>
      <div class="noise"></div>
    </div>

    <div class="auth-console">
      <div class="console-header">
        <h1 class="console-title">ACCESS CODE RESET</h1>
        <p class="console-subtitle">SECURITY CODE RESTORATION</p>
      </div>

      <div class="console-form">
        <div class="form-group">
          <label class="form-label">RECOVERY TOKEN</label>
          <input
            v-model="token"
            type="text"
            class="form-input"
            placeholder="ENTER RECOVERY CODE FROM EMAIL"
            @keyup.enter="handleResetPassword"
          />
        </div>

        <div class="form-group">
          <label class="form-label">NEW SECURITY CODE</label>
          <input
            v-model="newPassword"
            type="password"
            class="form-input"
            placeholder="ENTER NEW ACCESS CODE (MIN 6 CHARS)"
            @keyup.enter="handleResetPassword"
          />
        </div>

        <div class="form-group">
          <label class="form-label">CODE VERIFICATION</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="form-input"
            placeholder="REPEAT NEW SECURITY CODE"
            @keyup.enter="handleResetPassword"
          />
        </div>

        <button
          class="console-btn"
          :disabled="loading"
          @click="handleResetPassword"
        >
          <span v-if="!loading">EXECUTE CODE RESET</span>
          <span v-else>PROCESSING...</span>
        </button>
      </div>

      <div class="console-footer">
        <p>
          REMEMBER ACCESS CODE?
          <router-link to="/login" class="console-link"
            >RETURN TO TERMINAL</router-link
          >
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuthStore } from "@/stores/auth";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const token = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const loading = ref(false);

// 如果URL中有token参数，自动填充
if (route.query.token) {
  token.value = route.query.token;
}

const validateForm = () => {
  if (!token.value) {
    alert("RECOVERY TOKEN REQUIRED");
    return false;
  }
  if (!newPassword.value) {
    alert("NEW SECURITY CODE REQUIRED");
    return false;
  }
  if (newPassword.value.length < 6) {
    alert("SECURITY CODE MINIMUM 6 CHARACTERS");
    return false;
  }
  if (newPassword.value !== confirmPassword.value) {
    alert("SECURITY CODES DO NOT MATCH");
    return false;
  }
  return true;
};

const handleResetPassword = async () => {
  if (!validateForm()) return;

  loading.value = true;
  try {
    await authStore.resetPassword({
      token: token.value,
      newPassword: newPassword.value,
    });
    alert("ACCESS CODE RESET SUCCESSFUL - REDIRECTING TO TERMINAL");
    setTimeout(() => {
      router.push("/login");
    }, 1500);
  } catch (error) {
    alert(error.response?.data?.message || "RESET FAILED - SYSTEM ERROR");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.cassette-auth-terminal {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(
    135deg,
    var(--color-darkslate) 0%,
    var(--color-charcoal) 100%
  );
  position: relative;
  overflow: hidden;
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
  background: linear-gradient(
    to bottom,
    transparent 50%,
    rgba(0, 0, 0, 0.1) 51%
  );
  background-size: 100% 3px;
  animation: scanlines 0.1s linear infinite;
}

.noise {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.1'/%3E%3C/svg%3E");
  animation: noise 0.5s steps(10) infinite;
}

@keyframes scanlines {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(3px);
  }
}

@keyframes noise {
  0%,
  100% {
    transform: translate(0, 0);
  }
  10% {
    transform: translate(-1px, 1px);
  }
  20% {
    transform: translate(1px, -1px);
  }
  30% {
    transform: translate(-1px, -1px);
  }
  40% {
    transform: translate(1px, 1px);
  }
  50% {
    transform: translate(-1px, 0);
  }
  60% {
    transform: translate(1px, 0);
  }
  70% {
    transform: translate(0, 1px);
  }
  80% {
    transform: translate(0, -1px);
  }
  90% {
    transform: translate(-1px, 0);
  }
}

.auth-console {
  position: relative;
  z-index: 2;
  background: var(--color-eggshell);
  border: 3px solid var(--color-darkslate);
  box-shadow:
    0 0 0 1px var(--color-charcoal),
    4px 4px 0 var(--color-charcoal),
    8px 8px 20px rgba(0, 0, 0, 0.3);
  padding: 40px;
  max-width: 400px;
  width: 100%;
}

.console-header {
  text-align: center;
  margin-bottom: 32px;
  border-bottom: 2px solid var(--color-darkslate);
  padding-bottom: 16px;
}

.console-title {
  margin: 0 0 8px 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--color-charcoal);
  text-transform: uppercase;
  letter-spacing: 2px;
}

.console-subtitle {
  margin: 0;
  color: var(--color-darkslate);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.console-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--color-charcoal);
  text-transform: uppercase;
  font-size: 0.85rem;
  letter-spacing: 1px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--color-darkslate);
  background: var(--color-eggshell);
  color: var(--color-charcoal);
  font-family: "Courier New", monospace;
  font-size: 0.9rem;
  text-transform: uppercase;
  outline: none;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: var(--color-charcoal);
  box-shadow: 0 0 0 2px rgba(44, 62, 80, 0.2);
  transform: translateY(-1px);
}

.form-input::placeholder {
  color: var(--color-darkslate);
  opacity: 0.7;
}

.console-btn {
  width: 100%;
  padding: 16px;
  background: var(--color-charcoal);
  color: var(--color-eggshell);
  border: 2px solid var(--color-charcoal);
  font-family: "Courier New", monospace;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 8px;
}

.console-btn:hover:not(:disabled) {
  background: var(--color-darkslate);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.console-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.console-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.console-footer {
  text-align: center;
  border-top: 2px solid var(--color-darkslate);
  padding-top: 16px;
}

.console-footer p {
  margin: 0;
  color: var(--color-charcoal);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.console-link {
  color: var(--color-darkslate);
  text-decoration: none;
  font-weight: 600;
  border-bottom: 1px solid var(--color-darkslate);
  transition: all 0.2s ease;
}

.console-link:hover {
  color: var(--color-charcoal);
  border-bottom-color: var(--color-charcoal);
}

@media (max-width: 480px) {
  .auth-console {
    padding: 30px 20px;
    margin: 20px;
  }

  .console-title {
    font-size: 1.5rem;
  }

  .console-subtitle {
    font-size: 0.8rem;
  }

  .form-input,
  .console-btn {
    font-size: 0.85rem;
  }
}
</style>
