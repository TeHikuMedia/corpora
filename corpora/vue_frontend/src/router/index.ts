import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Pronunciation',
    component: () => import(/* webpackChunkName: "pronunciation" */ '../views/Pronunciation.vue')
  }
]

const router = createRouter({
  history: createWebHistory('/v/'),
  routes
})

export default router
