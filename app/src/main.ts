import Vue from 'vue'
import App from './App.vue'
import router from './router'

Vue.config.productionTip = false

// global state.  Use sparingly!
var shared = new Vue({
    data: () => {
      return {
        config: [],
        sshare: [],
        queue: [],
        myUser: "",
      }
    }
});

let eventBus = new Vue();

// Create a plugin to stop objects being observed
Vue.use({
    install: (Vue) => {
        //Object.defineProperty(Vue.prototype, '$noTrack', (o:object) => Object.preventExtensions(o))
        Object.defineProperty(Vue.prototype, '$global', {
              get: () => shared
          })
        Object.defineProperty(Vue.prototype, '$eventBus', {
              get: () => eventBus
        })
    }
})

new Vue({
  router,
  render: h => h(App),
}).$mount('#app')
