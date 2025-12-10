import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { io } from "socket.io-client";
import { useToast } from "vue-toastification";
import { useAuthStore } from "./auth";
import { useNotificationStore } from "./notification";

export const useSocketStore = defineStore("socket", () => {
  const toast = useToast();
  const authStore = useAuthStore();
  const notificationStore = useNotificationStore();

  // 状态
  const socket = ref(null);
  const isConnected = ref(false);
  const onlineCount = ref(0);
  const currentRoom = ref(null);
  const typingUsers = ref([]);

  // 计算属性
  const isAuthenticated = computed(() => authStore.isAuthenticated);
  const currentUser = computed(() => authStore.user);

  // 初始化Socket连接
  const initializeSocket = () => {
    if (!isAuthenticated.value || socket.value) return;

    const socketUrl = import.meta.env.VITE_SOCKET_URL || window.location.origin;

    socket.value = io(socketUrl, {
      auth: {
        token: authStore.accessToken,
      },
      transports: ["websocket", "polling"],
    });

    // 连接事件
    socket.value.on("connect", () => {
      console.log("Socket connected");
      isConnected.value = true;

      // 发送用户上线信息
      if (currentUser.value) {
        socket.value.emit("user_online", { user_id: currentUser.value.id });
      }
    });

    // 断开连接事件
    socket.value.on("disconnect", () => {
      console.log("Socket disconnected");
      isConnected.value = false;
      onlineCount.value = 0;
      typingUsers.value = [];
    });

    // 连接错误事件
    socket.value.on("connect_error", (error) => {
      console.error("Socket connection error:", error);
      isConnected.value = false;
    });

    // 在线用户计数
    socket.value.on("online_count", (data) => {
      onlineCount.value = data.count;
    });

    // 新评论事件
    socket.value.on("new_comment", (data) => {
      // 触发新评论事件，让相关组件处理
      window.dispatchEvent(
        new CustomEvent("socket:new-comment", { detail: data }),
      );
    });

    // 用户输入状态
    socket.value.on("user_typing", (data) => {
      const existingUser = typingUsers.value.find(
        (u) => u.user_id === data.user_id,
      );
      if (!existingUser) {
        typingUsers.value.push({
          user_id: data.user_id,
          post_id: data.post_id,
          timestamp: Date.now(),
        });
      }
    });

    socket.value.on("user_stop_typing", (data) => {
      typingUsers.value = typingUsers.value.filter(
        (u) => u.user_id !== data.user_id,
      );
    });

    // 新通知事件
    socket.value.on("new_notification", (notification) => {
      notificationStore.addNotification(notification);

      // 显示通知提示
      if (notification.title) {
        toast.info(`${notification.title}: ${notification.message}`);
      }
    });

    // 系统消息
    socket.value.on("system_message", (data) => {
      toast.info(data.message);
    });
  };

  // 断开Socket连接
  const disconnectSocket = () => {
    if (socket.value) {
      socket.value.disconnect();
      socket.value = null;
      isConnected.value = false;
      onlineCount.value = 0;
      typingUsers.value = [];
      currentRoom.value = null;
    }
  };

  // 加入房间
  const joinRoom = (roomId) => {
    if (!socket.value || !isConnected.value) return;

    // 如果已经在其他房间，先离开
    if (currentRoom.value) {
      leaveRoom(currentRoom.value);
    }

    socket.value.emit("join_post", { post_id: roomId });
    currentRoom.value = roomId;
  };

  // 离开房间
  const leaveRoom = (roomId) => {
    if (!socket.value || !isConnected.value) return;

    socket.value.emit("leave_post", { post_id: roomId });
    if (currentRoom.value === roomId) {
      currentRoom.value = null;
    }
  };

  // 发送输入状态
  const sendTypingStatus = (postId, isTyping = true) => {
    if (!socket.value || !isConnected.value || !currentUser.value) return;

    const event = isTyping ? "typing" : "stop_typing";
    socket.value.emit(event, {
      post_id: postId,
      user_id: currentUser.value.id,
    });
  };

  // 获取指定文章的输入用户
  const getTypingUsers = (postId) => {
    return typingUsers.value.filter((user) => user.post_id === postId);
  };

  // 清理超时的输入用户（超过5秒没有更新视为停止输入）
  const cleanupTypingUsers = () => {
    const now = Date.now();
    const timeout = 5000; // 5秒

    typingUsers.value = typingUsers.value.filter((user) => {
      return now - user.timestamp < timeout;
    });
  };

  // 发送自定义事件
  const emitEvent = (event, data) => {
    if (!socket.value || !isConnected.value) return;

    socket.value.emit(event, data);
  };

  // 监听自定义事件
  const onEvent = (event, callback) => {
    if (!socket.value) return;

    socket.value.on(event, callback);
  };

  // 移除事件监听
  const offEvent = (event, callback) => {
    if (!socket.value) return;

    socket.value.off(event, callback);
  };

  // 定期清理输入用户
  let cleanupInterval = null;

  const startCleanup = () => {
    if (cleanupInterval) return;

    cleanupInterval = setInterval(cleanupTypingUsers, 5000); // 每5秒清理一次
  };

  const stopCleanup = () => {
    if (cleanupInterval) {
      clearInterval(cleanupInterval);
      cleanupInterval = null;
    }
  };

  // 监听认证状态变化
  const watchAuthStatus = () => {
    // 如果用户登录了，初始化Socket
    if (isAuthenticated.value && !socket.value) {
      initializeSocket();
      startCleanup();
    }

    // 如果用户登出了，断开Socket
    if (!isAuthenticated.value && socket.value) {
      disconnectSocket();
      stopCleanup();
    }
  };

  return {
    socket,
    isConnected,
    onlineCount,
    currentRoom,
    typingUsers,
    initializeSocket,
    disconnectSocket,
    joinRoom,
    leaveRoom,
    sendTypingStatus,
    getTypingUsers,
    emitEvent,
    onEvent,
    offEvent,
    watchAuthStatus,
    cleanupTypingUsers,
  };
});
