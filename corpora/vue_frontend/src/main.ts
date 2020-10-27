import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faPlayCircle,
  faPauseCircle,
  faCheck,
  faCheckCircle,
  faTrash,
  faTimes
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(faPlayCircle)
library.add(faPauseCircle)
library.add(faCheck)
library.add(faCheckCircle)
library.add(faTrash)
library.add(faTimes)

createApp(App)
  .use(store)
  .use(router)
  .component('font-awesome-icon', FontAwesomeIcon)
  .mount('#app')
