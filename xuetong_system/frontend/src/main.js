import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Will be created in a subsequent step
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css' // Element Plus CSS
import './style.css' // Main global styles (Vite default)
import * as ElementPlusIconsVue from '@element-plus/icons-vue' // Import all icons

const app = createApp(App)

// Initialize Pinia state management
app.use(createPinia())

// Initialize Vue Router
app.use(router)

// Use Element Plus UI Library
app.use(ElementPlus)

// Register all Element Plus icons globally
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
