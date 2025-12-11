import { defineStore } from "pinia";
import { ref, computed } from "vue";
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
  const reconnectAttempts = ref(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3秒

  // 计算属性
  const isAuthenticated = computed(() => authStore.isAuthenticated);
  const currentUser = computed(() => authStore.user);

  // TCP客户端类
  class TCPClient {
    constructor(url) {
      this.url = url;
      this.ws = null;
      this.messageHandlers = new Map();
      this.reconnectTimer = null;
    }

    connect() {
      return new Promise((resolve, reject) => {
        try {
          this.ws = new WebSocket(this.url);
          
          this.ws.onopen = () => {
            console.log('TCP客户端连接成功');
            reconnectAttempts.value = 0;
            this.setupMessageHandling();
            
            // 发送认证信息
            if (isAuthenticated.value && currentUser.value) {
              this.sendMessage('authenticate', {
                user_id: currentUser.value.id,
                username: currentUser.value.username
              });
            }
            
            resolve();
          };

          this.ws.onclose = () => {
            console.log('TCP客户端连接关闭');
            isConnected.value = false;
            this.attemptReconnect();
          };

          this.ws.onerror = (error) => {
            console.error('TCP客户端连接错误:', error);
            reject(error);
          };

          this.ws.onmessage = (event) => {
            try {
              const message = JSON.parse(event.data);
              this.handleMessage(message);
            } catch (error) {
              console.error('消息解析错误:', error);
            }
          };

        } catch (error) {
          reject(error);
        }
      });
    }

    setupMessageHandling() {
      // 连接确认
      this.on('connected', (data) => {
        console.log('服务器连接确认:', data);
        isConnected.value = true;
      });

      // 认证成功
      this.on('auth_success', (data) => {
        console.log('认证成功:', data);
        this.joinRoom('global'); // 加入全局房间
      });

      // 认证失败
      this.on('auth_error', (data) => {
        console.error('认证失败:', data);
        toast.error('Socket认证失败');
      });

      // 在线用户数
      this.on('online_count', (data) => {
        onlineCount.value = data.count || 0;
      });

      // 新评论
      this.on('new_message', (data) => {
        if (data.message) {
          // 触发新评论事件，让相关组件处理
          window.dispatchEvent(
            new CustomEvent("socket:new-comment", { detail: data })
          );
        }
      });

      // 用户输入状态
      this.on('user_typing', (data) => {
        const existingUser = typingUsers.value.find(
          (u) => u.user_id === data.user_id
        );
        if (!existingUser) {
          typingUsers.value.push({
            user_id: data.user_id,
            post_id: data.post_id,
            timestamp: Date.now(),
          });
        }
      });

      this.on('user_stop_typing', (data) => {
        typingUsers.value = typingUsers.value.filter(
          (u) => u.user_id !== data.user_id
        );
      });

      // 系统消息
      this.on('system_message', (data) => {
        if (data.message) {
          toast.info(data.message);
        }
      });

      // 房间相关
      this.on('room_joined', (data) => {
        console.log('加入房间成功:', data);
        currentRoom.value = data.room_name;
      });

      this.on('user_joined', (data) => {
        console.log('用户加入房间:', data);
      });

      this.on('user_left', (data) => {
        console.log('用户离开房间:', data);
      });

      // 错误处理
      this.on('error', (data) => {
        console.error('Socket错误:', data);
        if (data.message) {
          toast.error(data.message);
        }
      });
    }

    handleMessage(message) {
      const handlers = this.messageHandlers.get(message.type) || [];
      handlers.forEach(handler => {
        try {
          handler(message.data);
        } catch (error) {
          console.error('消息处理错误:', error);
        }
      });
    }

    on(messageType, handler) {
      if (!this.messageHandlers.has(messageType)) {
        this.messageHandlers.set(messageType, []);
      }
      this.messageHandlers.get(messageType).push(handler);
    }

    off(messageType, handler) {
      const handlers = this.messageHandlers.get(messageType) || [];
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }

    sendMessage(type, data) {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        const message = {
          type: type,
          data: data
        };
        this.ws.send(JSON.stringify(message));
      } else {
        console.warn('WebSocket未连接，无法发送消息');
      }
    }

    attemptReconnect() {
      if (reconnectAttempts.value < maxReconnectAttempts) {
        reconnectAttempts.value++;
        console.log(`尝试重新连接 (${reconnectAttempts.value}/${maxReconnectAttempts})...`);
        
        this.reconnectTimer = setTimeout(() => {
          this.connect().catch(error => {
            console.error('重新连接失败:', error);
          });
        }, reconnectDelay);
      } else {
        console.error('达到最大重连次数，停止尝试');
        toast.error('Socket连接失败，请刷新页面重试');
      }
    }

    disconnect() {
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
      
      if (this.ws) {
        this.ws.close();
        this.ws = null;
      }
    }
  }

  // 初始化Socket连接
  const initializeSocket = async () => {
    if (!isAuthenticated.value || socket.value) return;

    try {
      const socketUrl = import.meta.env.VITE_SOCKET_URL || 'ws://localhost:8080';
      const client = new TCPClient(socketUrl);
      
      await client.connect();
      
      socket.value = client;
      
      // 启动清理定时器
      startCleanup();
      
    } catch (error) {
      console.error('Socket连接失败:', error);
      toast.error('实时连接失败');
    }
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
      
      if (cleanupInterval) {
        clearInterval(cleanupInterval);
        cleanupInterval = null;
      }
    }
  };

  // 加入房间
  const joinRoom = (roomId) => {
    if (!socket.value || !isConnected.value) return;

    // 如果已经在其他房间，先离开
    if (currentRoom.value) {
      leaveRoom(currentRoom.value);
    }

    socket.value.sendMessage('join_room', { room_name: roomId });
    currentRoom.value = roomId;
  };

  // 离开房间
  const leaveRoom = (roomId) => {
    if (!socket.value || !isConnected.value) return;

    socket.value.sendMessage('leave_room', { room_name: roomId });
    if (currentRoom.value === roomId) {
      currentRoom.value = null;
    }
  };

  // 发送输入状态
  const sendTypingStatus = (postId, isTyping = true) => {
    if (!socket.value || !isConnected.value || !currentUser.value) return;

    const event = isTyping ? 'typing' : 'stop_typing';
    socket.value.sendMessage(event, {
      room_name: postId,
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

    socket.value.sendMessage(event, data);
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

  return {
    // 状态
    socket,
    isConnected,
    onlineCount,
    currentRoom,
    typingUsers,
    reconnectAttempts,
    
    // 方法
    initializeSocket,
    disconnectSocket,
    joinRoom,
    leaveRoom,
    sendTypingStatus,
    getTypingUsers,
    cleanupTypingUsers,
    emitEvent,
    onEvent,
    offEvent,
  };
});