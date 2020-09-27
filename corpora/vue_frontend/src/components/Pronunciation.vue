<template>
  <div class="pronun">
    <h1>{{foo}}</h1>
    <p>{{recording}}</p>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { getRandomRecording } from '../api'
export default defineComponent({
  name: 'Pronunciation',
  data: function () {
    return {
      foo: 'bar',
      recording: {},
      error: null
    }
  },
  mounted: function () {
    console.log('mounted')
    getRandomRecording()
      .then((response) => {
        console.log(response)
        this.recording = 'test'
      })
      .catch((error) => {
        this.error = error
      })
  }
})
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
