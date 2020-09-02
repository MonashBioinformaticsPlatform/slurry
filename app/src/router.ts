import Vue from 'vue'
import Router from 'vue-router'
import Share from './views/Share.vue'
import Queue from './views/Queue.vue'
import Config from './views/Config.vue'
import Running from './views/Running.vue'
import PendingPlot from './views/PendingPlot.vue'
import QOS from './views/QOS.vue'

Vue.use(Router)

export default new Router({
  routes: [
    { path: '/share', name: 'share', component: Share },
    { path: '/queue', name: 'queue', component: Queue },
    { path: '/config', name: 'config', component: Config },
    { path: '/running', name: 'running', component: Running },
    { path: '/pending', name: 'pending', component: PendingPlot },
    { path: '/qos', name: 'qos', component: QOS },
    {
      path: '/about',
      name: 'about',
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import(/* webpackChunkName: "about" */ './views/About.vue')
    },
    { path: '*', redirect: '/queue' }
  ]
})
