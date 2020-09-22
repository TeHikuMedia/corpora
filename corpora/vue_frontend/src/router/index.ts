import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import Home from '../views/Home.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/pronunciation',
    name: 'Pronunciation',
    component: () => import(/* webpackChunkName: "pronunciation" */ '../views/Pronunciation.vue')
  }
]

const router = createRouter({
  history: createWebHistory('/v/'),
  routes
})

export default router
