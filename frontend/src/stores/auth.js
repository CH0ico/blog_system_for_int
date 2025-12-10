import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import api from "@/utils/api";

export const useAuthStore = defineStore("auth", () => {
  const router = useRouter();
  const toast = useToast();

  // 状态
  const user = ref(null);
  const accessToken = ref(localStorage.getItem("access_token") || null);
  const refreshToken = ref(localStorage.getItem("refresh_token") || null);
  const isLoading = ref(false);

  // 计算属性
  const isAuthenticated = computed(() => !!user.value && !!accessToken.value);
  const userPermissions = computed(() => user.value?.permissions || []);
  const isAdmin = computed(() => user.value?.is_admin || false);

  // 登录
  const login = async (credentials) => {
    isLoading.value = true;
    try {
      const response = await api.post("/auth/login", credentials);
      const {
        user: userData,
        permissions,
        access_token,
        refresh_token,
      } = response.data;
      user.value = {
        ...userData,
        permissions: permissions || userData.permissions || [],
      };
      accessToken.value = access_token;
      refreshToken.value = refresh_token;

      // 保存到localStorage
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);

      // 设置API请求头
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

      toast.success("登录成功");
      router.push("/");

      return response.data;
    } catch (error) {
      const message = error.response?.data?.message || "登录失败";
      toast.error(message);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  // 注册
  const register = async (userData) => {
    isLoading.value = true;
    try {
      const response = await api.post("/auth/register", userData);
      const {
        user: userInfo,
        permissions,
        access_token,
        refresh_token,
      } = response.data;
      user.value = {
        ...userInfo,
        permissions: permissions || userInfo.permissions || [],
      };
      accessToken.value = access_token;
      refreshToken.value = refresh_token;

      // 保存到localStorage
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);

      // 设置API请求头
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;

      toast.success("注册成功");
      router.push("/");

      return response.data;
    } catch (error) {
      const message = error.response?.data?.message || "注册失败";
      toast.error(message);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  // 登出
  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // 清除状态
      user.value = null;
      accessToken.value = null;
      refreshToken.value = null;

      // 清除localStorage
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      // 清除请求头
      delete api.defaults.headers.common["Authorization"];

      toast.success("已登出");
      router.push("/login");
    }
  };

  // 获取当前用户信息
  const fetchUser = async () => {
    if (!accessToken.value) return;

    try {
      const response = await api.get("/auth/me");
      const perms =
        response.data.permissions || response.data.user?.permissions || [];
      user.value = { ...response.data.user, permissions: perms };
      return response.data.user;
    } catch (error) {
      // 如果获取用户信息失败，可能是token无效
      if (error.response?.status === 401) {
        await logout();
      }
      throw error;
    }
  };

  // 更新用户资料
  const updateProfile = async (profileData) => {
    isLoading.value = true;
    try {
      const response = await api.put("/auth/me", profileData);
      user.value = response.data.user;
      toast.success("资料更新成功");
      return response.data;
    } catch (error) {
      const message = error.response?.data?.message || "更新失败";
      toast.error(message);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  // 修改密码
  const changePassword = async (passwordData) => {
    isLoading.value = true;
    try {
      const response = await api.put("/auth/change-password", passwordData);
      toast.success("密码修改成功");
      return response.data;
    } catch (error) {
      const message = error.response?.data?.message || "修改失败";
      toast.error(message);
      throw error;
    } finally {
      isLoading.value = false;
    }
  };

  // 检查认证状态
  const checkAuthStatus = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return false;

    try {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      await fetchUser();
      return true;
    } catch (error) {
      // 如果检查失败，清除认证信息
      await logout();
      return false;
    }
  };

  // 检查权限
  const hasPermission = (permission) => {
    if (isAdmin.value) return true;
    return userPermissions.value.includes(permission);
  };

  // 忘记密码
  const forgotPassword = async (email) => {
    try {
      const response = await api.post("/auth/forgot-password", { email });
      const link = response.data.reset_link;
      toast.success(link ? "已生成重置链接" : "重置邮件已发送");
      return response.data;
    } catch (error) {
      const message = error.response?.data?.message || "发送失败";
      toast.error(message);
      throw error;
    }
  };

  // 重置密码
  const resetPassword = async (token, newPassword) => {
    try {
      const response = await api.post("/auth/reset-password", {
        token,
        new_password: newPassword,
      });
      toast.success("密码重置成功");
      return response.data;
    } catch (error) {
      const message = error.response?.data?.message || "重置失败";
      toast.error(message);
      throw error;
    }
  };

  // 检查用户名是否可用
  const checkUsername = async (username) => {
    try {
      const response = await api.get("/auth/check-username", {
        params: { username },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  // 检查邮箱是否可用
  const checkEmail = async (email) => {
    try {
      const response = await api.get("/auth/check-email", {
        params: { email },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  // 初始化
  const initialize = () => {
    const token = localStorage.getItem("access_token");
    if (token) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
      checkAuthStatus();
    }
  };

  return {
    user,
    accessToken,
    refreshToken,
    isLoading,
    isAuthenticated,
    userPermissions,
    isAdmin,
    login,
    register,
    logout,
    fetchUser,
    updateProfile,
    changePassword,
    checkAuthStatus,
    hasPermission,
    forgotPassword,
    resetPassword,
    checkUsername,
    checkEmail,
    initialize,
  };
});
