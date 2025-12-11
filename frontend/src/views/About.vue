<template>
  <div class="cassette-about-terminal">
    <div class="about-container">
      <!-- 页面头部 -->
      <header class="about-header">
        <div class="header-content">
          <h1>PROJECT INSIGHT</h1>
          <p>ABOUT THE SYSTEM</p>
        </div>
      </header>

      <!-- 主要内容 -->
      <main class="about-content">
        <!-- 介绍部分 -->
        <section class="about-section">
          <div class="section-header">
            <span class="section-label">SYSTEM OVERVIEW</span>
          </div>
          <div class="section-card">
            <h2>WELCOME TO OUR BLOG SYSTEM</h2>
            <p>
              THIS IS A MODERN BLOG PLATFORM DESIGNED TO PROVIDE USERS WITH A
              CLEAN, EFFICIENT WRITING AND READING ENVIRONMENT. WE BELIEVE
              EVERYONE HAS THE RIGHT TO SHARE KNOWLEDGE AND EXPERIENCE, SO WE
              CREATED THIS PLATFORM, ALLOWING EVERYONE TO EASILY EXPRESS THEIR
              VIEWS AND SHARE THEIR IDEAS WITH THE WORLD.
            </p>
          </div>
        </section>

        <!-- 使命部分 -->
        <section class="mission-section">
          <div class="section-header">
            <span class="section-label">OUR MISSION</span>
          </div>
          <div class="section-card">
            <h3>OUR MISSION</h3>
            <p>
              OUR MISSION IS TO CREATE AN OPEN, FRIENDLY COMMUNITY WHERE
              KNOWLEDGE CAN FLOW FREELY. WHETHER YOU'RE A TECH EXPERT, A LIFE
              ENTHUSIAST, OR A BEGINNER, THIS IS THE IDEAL PLACE FOR YOU TO
              SHOWCASE YOUR TALENTS, LEARN, AND GROW.
            </p>
          </div>
        </section>

        <!-- 特色部分 -->
        <section class="features-section">
          <div class="section-header">
            <span class="section-label">SYSTEM FEATURES</span>
          </div>
          <div class="section-card">
            <h3>PLATFORM FEATURES</h3>
            <div class="features-grid">
              <div class="feature-item">
                <div class="feature-icon">🔧</div>
                <div class="feature-content">
                  <h4>INTUITIVE DESIGN</h4>
                  <p>
                    INTUITIVE INTERFACE DESIGN, ALLOWING YOU TO FOCUS ON CONTENT
                    CREATION
                  </p>
                </div>
              </div>
              <div class="feature-item">
                <div class="feature-icon">🛠️</div>
                <div class="feature-content">
                  <h4>RICH FUNCTIONS</h4>
                  <p>
                    SUPPORT FOR ARTICLE CATEGORIES, TAG MANAGEMENT, COMMENT
                    INTERACTION, AND MORE
                  </p>
                </div>
              </div>
              <div class="feature-item">
                <div class="feature-icon">📱</div>
                <div class="feature-content">
                  <h4>RESPONSIVE DESIGN</h4>
                  <p>
                    PERFECTLY ADAPTED TO VARIOUS DEVICES, ACCESSIBLE ANYTIME,
                    ANYWHERE
                  </p>
                </div>
              </div>
              <div class="feature-item">
                <div class="feature-icon">🔒</div>
                <div class="feature-content">
                  <h4>SAFE AND RELIABLE</h4>
                  <p>ADOPT MODERN SECURITY TECHNOLOGY TO PROTECT YOUR DATA</p>
                </div>
              </div>
              <div class="feature-item">
                <div class="feature-icon">👥</div>
                <div class="feature-content">
                  <h4>COMMUNITY INTERACTION</h4>
                  <p>INTERACT WITH OTHER AUTHORS AND GROW TOGETHER</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 技术架构 -->
        <section class="tech-section">
          <div class="section-header">
            <span class="section-label">TECHNICAL ARCHITECTURE</span>
          </div>
          <div class="section-card">
            <h3>TECHNOLOGY STACK</h3>
            <p>OUR BLOG SYSTEM IS BUILT WITH MODERN TECHNOLOGY STACK:</p>
            <div class="tech-stack-grid">
              <div class="tech-item">
                <div class="tech-icon">🖥️</div>
                <div class="tech-content">
                  <h4>FRONTEND</h4>
                  <p>VUE 3 + ELEMENT PLUS + VITE</p>
                </div>
              </div>
              <div class="tech-item">
                <div class="tech-icon">⚙️</div>
                <div class="tech-content">
                  <h4>BACKEND</h4>
                  <p>NODE.JS + EXPRESS + MYSQL</p>
                </div>
              </div>
              <div class="tech-item">
                <div class="tech-icon">🚀</div>
                <div class="tech-content">
                  <h4>DEPLOYMENT</h4>
                  <p>DOCKER + NGINX</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 联系我们 -->
        <section class="contact-section">
          <div class="section-header">
            <span class="section-label">CONTACT INFORMATION</span>
          </div>
          <div class="section-card">
            <h3>CONTACT US</h3>
            <p>
              IF YOU HAVE ANY QUESTIONS, SUGGESTIONS OR FEEDBACK, PLEASE CONTACT
              US VIA THE FOLLOWING METHODS:
            </p>
            <div class="contact-info">
              <div class="contact-item">
                <span class="contact-icon">📧</span>
                <span class="contact-text">EMAIL: CONTACT@BLOG-SYSTEM.COM</span>
              </div>
              <div class="contact-item">
                <span class="contact-icon">🐙</span>
                <span class="contact-text"
                  >GITHUB:
                  <a href="#" target="_blank">GITHUB.COM/BLOG-SYSTEM</a></span
                >
              </div>
              <div class="contact-item">
                <span class="contact-icon">🌐</span>
                <span class="contact-text"
                  >COMMUNITY:
                  <a href="#" target="_blank"
                    >COMMUNITY.BLOG-SYSTEM.COM</a
                  ></span
                >
              </div>
            </div>
          </div>
        </section>

        <!-- 行动号召 -->
        <section class="cta-section">
          <div class="section-header">
            <span class="section-label">GET INVOLVED</span>
          </div>
          <div class="section-card">
            <div class="cta-buttons">
              <button
                class="cta-btn primary"
                @click="$router.push('/register')"
              >
                <span class="btn-icon">✎</span>
                START WRITING
              </button>
              <button class="cta-btn secondary" @click="$router.push('/posts')">
                <span class="btn-icon">📄</span>
                BROWSE ARTICLES
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
// 关于页面不需要特殊的逻辑处理
</script>

<style scoped>
.cassette-about-terminal {
  position: relative;
  min-height: 100vh;
  background-color: #f5f0e6;
  background-image:
    linear-gradient(rgba(0, 0, 0, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
  color: #2c2c2c;
  font-family: "Courier New", monospace;
  overflow: hidden;
}

.about-container {
  position: relative;
  z-index: 2;
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 20px;
}

/* 页面头部 */
.about-header {
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 4px 4px 0 #e67e22;
  padding: 30px;
  margin-bottom: 40px;
  position: relative;
  text-align: center;
}

.about-header::before {
  content: "ABOUT SYSTEM";
  position: absolute;
  top: -10px;
  left: 10px;
  background: #e67e22;
  color: white;
  padding: 5px 15px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 2px 2px 0 #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.header-content h1 {
  font-size: 2.5rem;
  font-weight: 900;
  color: #2c2c2c;
  margin: 0 0 10px 0;
  letter-spacing: 3px;
  text-transform: uppercase;
}

.header-content p {
  font-size: 14px;
  color: #2c2c2c;
  opacity: 0.8;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600;
}

/* 主要内容 */
.about-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* 章节头部 */
.section-header {
  margin-bottom: 25px;
}

.section-label {
  background: #e67e22;
  color: white;
  padding: 8px 15px;
  font-size: 12px;
  font-weight: bold;
  box-shadow: 2px 2px 0 #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 章节卡片 */
.section-card {
  background: white;
  border: 2px solid #2c2c2c;
  box-shadow: 3px 3px 0 #2c2c2c;
  padding: 30px;
  transition: all 0.2s ease;
}

.section-card:hover {
  box-shadow: 5px 5px 0 #e67e22;
  transform: translate(-2px, -2px);
}

/* 标题样式 */
.section-card h2 {
  font-size: 1.8rem;
  font-weight: 900;
  color: #2c2c2c;
  margin: 0 0 20px 0;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.section-card h3 {
  font-size: 1.4rem;
  font-weight: 900;
  color: #2c2c2c;
  margin: 0 0 15px 0;
  text-transform: uppercase;
  letter-spacing: 1px;
  border-bottom: 2px solid #e67e22;
  padding-bottom: 10px;
  display: inline-block;
}

.section-card h4 {
  font-size: 1.1rem;
  font-weight: 900;
  color: #2c2c2c;
  margin: 0 0 8px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* 段落样式 */
.section-card p {
  margin: 0 0 16px 0;
  line-height: 1.8;
  color: #2c2c2c;
  font-size: 14px;
  text-align: justify;
}

/* 特色功能网格 */
.features-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
  margin-top: 20px;
}

.feature-item {
  display: flex;
  gap: 15px;
  align-items: flex-start;
  padding: 15px;
  background: #fff9ed;
  border: 1px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  transition: all 0.2s ease;
}

.feature-item:hover {
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
}

.feature-icon {
  font-size: 24px;
  margin-top: 2px;
  flex-shrink: 0;
}

.feature-content {
  flex: 1;
}

.feature-content p {
  margin: 0;
  font-size: 12px;
  opacity: 0.9;
}

/* 技术栈网格 */
.tech-stack-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.tech-item {
  display: flex;
  gap: 15px;
  align-items: center;
  padding: 20px;
  background: #fff9ed;
  border: 2px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  transition: all 0.2s ease;
}

.tech-item:hover {
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
}

.tech-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.tech-content {
  flex: 1;
}

.tech-content p {
  margin: 0;
  font-size: 12px;
  opacity: 0.9;
}

/* 联系信息 */
.contact-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fff9ed;
  border: 1px solid #2c2c2c;
  box-shadow: 2px 2px 0 #2c2c2c;
  transition: all 0.2s ease;
}

.contact-item:hover {
  box-shadow: 3px 3px 0 #e67e22;
  transform: translate(-1px, -1px);
}

.contact-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.contact-text {
  font-size: 14px;
  color: #2c2c2c;
}

.contact-text a {
  color: #e67e22;
  text-decoration: none;
  border-bottom: 1px dashed #e67e22;
  transition: all 0.2s ease;
}

.contact-text a:hover {
  background: #e67e22;
  color: white;
  padding: 2px 5px;
  border-bottom: none;
  box-shadow: 1px 1px 0 #2c2c2c;
}

/* 行动号召按钮 */
.cta-buttons {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: 2px solid #2c2c2c;
  background: white;
  color: #2c2c2c;
  font-family: "Courier New", monospace;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.1s ease;
  box-shadow: 2px 2px 0 #2c2c2c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  min-width: 180px;
  justify-content: center;
}

.cta-btn.primary {
  background: #e67e22;
  color: white;
}

.cta-btn.secondary {
  background: white;
  color: #2c2c2c;
}

.cta-btn:hover {
  box-shadow: 3px 3px 0 #2c2c2c;
  transform: translate(-1px, -1px);
}

.cta-btn.primary:hover {
  background: #d35400;
}

.cta-btn.secondary:hover {
  background: #f8f8f8;
}

.cta-btn:active {
  box-shadow: 1px 1px 0 #2c2c2c;
  transform: translate(0, 0);
}

.btn-icon {
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .about-container {
    padding: 20px 15px;
  }

  .about-header,
  .section-card {
    padding: 20px;
  }

  .header-content h1 {
    font-size: 2rem;
  }

  .section-card h2 {
    font-size: 1.5rem;
  }

  .section-card h3 {
    font-size: 1.2rem;
  }

  .tech-stack-grid {
    grid-template-columns: 1fr;
  }

  .cta-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .cta-btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .header-content h1 {
    font-size: 1.5rem;
  }

  .section-card {
    padding: 15px;
  }

  .feature-item,
  .tech-item {
    flex-direction: column;
    text-align: center;
  }

  .feature-icon,
  .tech-icon {
    margin-top: 0;
  }
}
</style>
