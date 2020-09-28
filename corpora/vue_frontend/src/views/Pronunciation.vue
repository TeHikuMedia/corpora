<template>
  <div class="pronunciation">
    <Pronunciation />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import Pronunciation from '@/components/Pronunciation.vue' // @ is an alias to /src

export default defineComponent({
  name: 'PronunciationView',
  components: {
    Pronunciation
  }
})
</script>
