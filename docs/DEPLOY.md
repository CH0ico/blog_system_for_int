# 博客系统部署指南

## 环境要求

### 开发环境
- Python 3.8+
- Node.js 14+
- SQLite (默认)

### 生产环境
- Python 3.8+
- Node.js 14+
- MySQL 5.7+ 或 PostgreSQL 12+
- Nginx (反向代理)
- Redis (可选，用于缓存和会话)

## 开发环境部署

### 后端部署

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd blog_system/backend
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   # 创建 .env 文件
   cp .env.example .env
   
   # 编辑 .env 文件
   nano .env
   ```

   **环境变量配置:**
   ```env
   # Flask配置
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   
   # 数据库配置
   DATABASE_URL=sqlite:///blog.db
   # 或者使用MySQL
   # DATABASE_URL=mysql+pymysql://username:password@localhost/blog_db
   
   # CORS配置
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   
   # 邮件配置
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   ```

5. **初始化数据库**
   ```bash
   python app.py init-db
   ```

6. **运行开发服务器**
   ```bash
   python app.py
   ```

   后端服务将在 `http://localhost:5000` 启动

### 前端部署

1. **进入前端目录**
   ```bash
   cd ../frontend
   ```

2. **安装依赖**
   ```bash
   npm install
   ```

3. **配置环境变量**
   ```bash
   # 创建 .env 文件
   cp .env.example .env
   
   # 编辑 .env 文件
   nano .env
   ```

   **环境变量配置:**
   ```env
   VITE_API_BASE_URL=http://localhost:5000/api
   VITE_SOCKET_URL=http://localhost:5000
   ```

4. **运行开发服务器**
   ```bash
   npm run dev
   ```

   前端服务将在 `http://localhost:3000` 启动

## 生产环境部署

### 后端部署

1. **服务器准备**
   ```bash
   # 更新系统
   sudo apt update && sudo apt upgrade -y
   
   # 安装Python和pip
   sudo apt install python3 python3-pip python3-venv -y
   
   # 安装MySQL（如果使用MySQL）
   sudo apt install mysql-server -y
   
   # 安装Redis（可选）
   sudo apt install redis-server -y
   ```

2. **数据库配置**
   ```bash
   # MySQL配置
   sudo mysql_secure_installation
   
   # 登录MySQL
   sudo mysql -u root -p
   
   # 创建数据库
   CREATE DATABASE blog_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   # 创建用户
   CREATE USER 'blog_user'@'localhost' IDENTIFIED BY 'secure_password';
   
   # 授权
   GRANT ALL PRIVILEGES ON blog_db.* TO 'blog_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **应用部署**
   ```bash
   # 创建应用目录
   sudo mkdir -p /var/www/blog
   sudo chown -R $USER:$USER /var/www/blog
   
   # 克隆项目
   cd /var/www/blog
   git clone <repository-url> .
   
   # 后端配置
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # 配置生产环境变量
   cp .env.production.example .env.production
   nano .env.production
   ```

4. **使用Gunicorn运行**
   ```bash
   # 安装Gunicorn
   pip install gunicorn
   
   # 创建启动脚本
   cat > start.sh << 'EOF'
   #!/bin/bash
   source venv/bin/activate
   export FLASK_ENV=production
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   EOF
   
   chmod +x start.sh
   ```

5. **使用Systemd管理服务**
   ```bash
   sudo nano /etc/systemd/system/blog-backend.service
   ```

   **服务配置:**
   ```ini
   [Unit]
   Description=Blog Backend
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/blog/backend
   Environment=FLASK_ENV=production
   ExecStart=/var/www/blog/backend/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl enable blog-backend
   sudo systemctl start blog-backend
   ```

### 前端部署

1. **构建生产版本**
   ```bash
   cd /var/www/blog/frontend
   npm install
   npm run build
   ```

2. **Nginx配置**
   ```bash
   sudo nano /etc/nginx/sites-available/blog
   ```

   **Nginx配置:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       # 前端静态文件
       location / {
           root /var/www/blog/frontend/dist;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       # API代理
       location /api {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_cache_bypass $http_upgrade;
       }
       
       # WebSocket代理
       location /socket.io {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
       
       # 静态资源缓存
       location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
           root /var/www/blog/frontend/dist;
           expires 1y;
           add_header Cache-Control "public, immutable";
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### SSL证书配置

1. **安装Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   ```

2. **获取SSL证书**
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **自动续期**
   ```bash
   sudo crontab -e
   ```

   添加以下内容:
   ```
   0 0 * * * /usr/bin/certbot renew --quiet
   ```

## Docker部署

### Docker Compose配置

1. **创建docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx.conf:/etc/nginx/nginx.conf
         - ./frontend/dist:/usr/share/nginx/html
         - ./ssl:/etc/nginx/ssl
       depends_on:
         - backend
       restart: always
     
     backend:
       build: ./backend
       ports:
         - "5000:5000"
       environment:
         - FLASK_ENV=production
         - DATABASE_URL=mysql+pymysql://blog_user:password@mysql/blog_db
         - SECRET_KEY=your-secret-key
         - JWT_SECRET_KEY=your-jwt-secret-key
       depends_on:
         - mysql
         - redis
       restart: always
     
     mysql:
       image: mysql:8.0
       environment:
         - MYSQL_ROOT_PASSWORD=root_password
         - MYSQL_DATABASE=blog_db
         - MYSQL_USER=blog_user
         - MYSQL_PASSWORD=password
       volumes:
         - mysql_data:/var/lib/mysql
       restart: always
     
     redis:
       image: redis:alpine
       restart: always
   
   volumes:
     mysql_data:
   ```

2. **构建和运行**
   ```bash
   docker-compose up -d
   ```

## 监控和维护

### 日志管理

1. **应用日志**
   ```bash
   # 查看后端日志
   sudo journalctl -u blog-backend -f
   
   # 查看Nginx日志
   sudo tail -f /var/log/nginx/access.log
   sudo tail -f /var/log/nginx/error.log
   ```

2. **日志轮转**
   ```bash
   sudo nano /etc/logrotate.d/blog
   ```

   ```
   /var/log/nginx/blog-*.log {
       daily
       missingok
       rotate 52
       compress
       delaycompress
       notifempty
       create 644 www-data www-data
   }
   ```

### 备份策略

1. **数据库备份**
   ```bash
   # 创建备份脚本
   nano backup.sh
   ```

   ```bash
   #!/bin/bash
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="/var/backups/blog"
   
   mkdir -p $BACKUP_DIR
   
   # 备份数据库
   mysqldump -u blog_user -p blog_db > $BACKUP_DIR/blog_db_$DATE.sql
   
   # 备份上传文件
   tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/blog/backend/uploads/
   
   # 删除30天前的备份
   find $BACKUP_DIR -type f -mtime +30 -delete
   ```

   ```bash
   chmod +x backup.sh
   
   # 添加到crontab
   crontab -e
   ```

   ```
   0 2 * * * /var/www/blog/backup.sh
   ```

### 性能优化

1. **数据库优化**
   ```sql
   -- 添加必要的索引
   CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
   CREATE INDEX idx_posts_view_count ON posts(view_count DESC);
   CREATE INDEX idx_comments_post_id_created_at ON comments(post_id, created_at DESC);
   ```

2. **Redis缓存配置**
   ```bash
   # 编辑Redis配置
   sudo nano /etc/redis/redis.conf
   
   # 添加以下配置
   maxmemory 256mb
   maxmemory-policy allkeys-lru
   maxmemory-samples 3
   ```

3. **Nginx优化**
   ```nginx
   # 在http块中添加
   gzip on;
   gzip_vary on;
   gzip_min_length 1024;
   gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
   
   # 缓存配置
   location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

## 故障排查

### 常见问题

1. **数据库连接失败**
   - 检查数据库服务是否运行
   - 验证数据库连接配置
   - 检查防火墙设置

2. **前端无法访问API**
   - 检查CORS配置
   - 验证Nginx代理设置
   - 检查防火墙端口

3. **WebSocket连接失败**
   - 检查Nginx WebSocket代理配置
   - 验证Socket.IO版本兼容性

4. **内存不足**
   - 增加服务器内存
   - 优化数据库查询
   - 启用Redis缓存

### 监控工具

1. **系统监控**
   ```bash
   # 安装htop
   sudo apt install htop
   
   # 安装iotop
   sudo apt install iotop
   ```

2. **应用监控**
   ```python
   # 使用Flask-MonitoringDashboard
   pip install flask-monitoringdashboard
   ```

3. **数据库监控**
   ```sql
   -- 查看慢查询
   SHOW PROCESSLIST;
   
   -- 查看表状态
   SHOW TABLE STATUS;
   ```

## 安全建议

1. **定期更新**
   ```bash
   # 更新系统包
   sudo apt update && sudo apt upgrade -y
   
   # 更新Python包
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **安全配置**
   - 使用强密码
   - 定期更换密钥
   - 启用防火墙
   - 配置SSL证书
   - 限制SSH访问

3. **备份验证**
   - 定期测试备份恢复
   - 验证备份数据完整性
   - 异地存储备份

## 扩展功能

1. **CDN配置**
   - 使用Cloudflare或AWS CloudFront
   - 配置静态资源CDN

2. **负载均衡**
   - 使用Nginx负载均衡
   - 配置多个后端实例

3. **微服务架构**
   - 拆分服务功能
   - 使用Docker容器化
   - 配置服务发现

## 技术支持

如有问题，请联系:
- 邮箱: support@blog.com
- 文档: https://docs.blog.com
- 社区: https://community.blog.com