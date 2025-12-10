import axios from "axios";
import { useToast } from "vue-toastification";

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const toast = useToast();

    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 401:
          // Token过期或无效
          if (data.error === "token_expired") {
            // 尝试刷新token
            try {
              const refreshToken = localStorage.getItem("refresh_token");
              if (refreshToken) {
                const refreshResponse = await api.post("/auth/refresh", {
                  refresh_token: refreshToken,
                });

                const { access_token } = refreshResponse.data;
                localStorage.setItem("access_token", access_token);

                // 重试原请求
                error.config.headers.Authorization = `Bearer ${access_token}`;
                return api.request(error.config);
              }
            } catch (refreshError) {
              // 刷新失败，清除认证信息
              localStorage.removeItem("access_token");
              localStorage.removeItem("refresh_token");
              window.location.href = "/login";
            }
          } else {
            // 其他401错误
            toast.error("请重新登录");
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            window.location.href = "/login";
          }
          break;

        case 403:
          toast.error("没有权限访问此资源");
          break;

        case 404:
          toast.error("请求的资源不存在");
          break;

        case 422:
          // 验证错误
          const errors = data.errors || {};
          const firstError =
            Object.values(errors)[0]?.[0] || data.message || "请求数据验证失败";
          toast.error(firstError);
          break;

        case 429:
          toast.error("请求过于频繁，请稍后再试");
          break;

        case 500:
          toast.error("服务器内部错误，请稍后重试");
          break;

        default:
          toast.error(data.message || "请求失败");
      }
    } else if (error.request) {
      // 网络错误
      toast.error("网络连接失败，请检查网络设置");
    } else {
      // 其他错误
      toast.error("请求发生错误");
    }

    return Promise.reject(error);
  },
);

export default api;
