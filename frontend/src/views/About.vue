<template>
  <div class="about-page">
    <div class="container">
      <div class="about-content">
        <div class="about-header">
          <h1>关于我们</h1>
          <p>了解我们的故事和使命</p>
        </div>
        
        <div class="about-section">
          <div class="section-content">
            <h2>欢迎来到我们的博客系统</h2>
            <p>
              这是一个现代化的博客平台，旨在为用户提供一个简洁、高效的写作和阅读环境。
              我们相信每个人都有分享知识和经验的权利，因此我们创建了这个平台，
              让每个人都能轻松地表达自己的观点，与全世界分享自己的想法。
            </p>
            
            <h3>我们的使命</h3>
            <p>
              我们的使命是创建一个开放、友好的社区，让知识可以自由流动。
              无论你是技术专家、生活达人，还是刚刚起步的新手，
              这里都是你展示才华、学习成长的理想场所。
            </p>
            
            <h3>平台特色</h3>
            <ul>
              <li><strong>简洁易用：</strong>直观的界面设计，让你专注于内容创作</li>
              <li><strong>功能丰富：</strong>支持文章分类、标签管理、评论互动等功能</li>
              <li><strong>响应式设计：</strong>完美适配各种设备，随时随地访问</li>
              <li><strong>安全可靠：</strong>采用现代化的安全技术，保护你的数据</li>
              <li><strong>社区互动：</strong>与其他作者交流，共同成长</li>
            </ul>
            
            <h3>技术架构</h3>
            <p>
              我们的博客系统采用现代化的技术栈构建：
            </p>
            <div class="tech-stack">
              <div class="tech-item">
                <h4>前端</h4>
                <p>Vue 3 + Element Plus + Vite</p>
              </div>
              <div class="tech-item">
                <h4>后端</h4>
                <p>Node.js + Express + MySQL</p>
              </div>
              <div class="tech-item">
                <h4>部署</h4>
                <p>Docker + Nginx</p>
              </div>
            </div>
            
            <h3>联系我们</h3>
            <p>
              如果你有任何问题、建议或反馈，欢迎通过以下方式联系我们：
            </p>
            <div class="contact-info">
              <p><strong>邮箱：</strong>contact@blog-system.com</p>
              <p><strong>GitHub：</strong><a href="#" target="_blank">github.com/blog-system</a></p>
              <p><strong>社区：</strong><a href="#" target="_blank">community.blog-system.com</a></p>
            </div>
            
            <div class="cta-section">
              <el-button type="primary" size="large" @click="$router.push('/register')">
                立即开始写作
              </el-button>
              <el-button size="large" @click="$router.push('/posts')">
                浏览文章
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 关于页面不需要特殊的逻辑处理
</script>

<style scoped>
.about-page {
  min-height: 100vh;
  padding: 40px 0;
  background-color: var(--el-bg-color-page);
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px;
}

.about-content {
  background: white;
  border-radius: 12px;
  padding: 60px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.about-header {
  text-align: center;
  margin-bottom: 48px;
}

.about-header h1 {
  margin: 0 0 16px 0;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
}

.about-header p {
  margin: 0;
  font-size: 1.1rem;
  color: var(--el-text-color-secondary);
}

.about-section h2 {
  margin: 0 0 24px 0;
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.about-section h3 {
  margin: 32px 0 16px 0;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.about-section p {
  margin: 0 0 16px 0;
  line-height: 1.8;
  color: var(--el-text-color-regular);
}

.about-section ul {
  margin: 16px 0;
  padding-left: 24px;
}

.about-section li {
  margin: 8px 0;
  line-height: 1.6;
  color: var(--el-text-color-regular);
}

.tech-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin: 24px 0;
}

.tech-item {
  background: var(--el-fill-color-light);
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.tech-item h4 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  color: var(--el-text-color-primary);
}

.tech-item p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 0.9rem;
}

.contact-info {
  background: var(--el-fill-color-lighter);
  padding: 20px;
  border-radius: 8px;
  margin: 16px 0;
}

.contact-info p {
  margin: 8px 0;
  color: var(--el-text-color-regular);
}

.contact-info a {
  color: var(--el-color-primary);
  text-decoration: none;
}

.contact-info a:hover {
  text-decoration: underline;
}

.cta-section {
  text-align: center;
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.cta-section .el-button {
  margin: 0 12px;
}

@media (max-width: 768px) {
  .about-content {
    padding: 40px 30px;
  }
  
  .about-header h1 {
    font-size: 2rem;
  }
  
  .about-section h2 {
    font-size: 1.5rem;
  }
  
  .tech-stack {
    grid-template-columns: 1fr;
  }
  
  .cta-section .el-button {
    display: block;
    width: 100%;
    margin: 12px 0;
  }
}

@media (max-width: 480px) {
  .about-content {
    padding: 30px 20px;
  }
  
  .about-header h1 {
    font-size: 1.8rem;
  }
}
</style>