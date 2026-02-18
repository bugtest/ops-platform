<template>
  <div class="app">
    <header class="header">
      <div class="header-content">
        <h1 class="logo">🐙 智能运维平台</h1>
        <nav class="nav">
          <router-link to="/chat" class="nav-link">对话</router-link>
          <router-link to="/plugins" class="nav-link">插件</router-link>
        </nav>
      </div>
    </header>
    <main class="main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 20px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.logo {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.nav {
  display: flex;
  gap: 20px;
}

.nav-link {
  color: #6b7280;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-link:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.nav-link.router-link-active {
  background: #eff6ff;
  color: #3b82f6;
}

.main {
  flex: 1;
  padding: 20px;
}
</style>
