<template>
  <div class="button">
    <div class="icon">
      <font-awesome-icon v-if="icon !== null" :icon="icon" fixed-width v-on:click="clicked" />
    </div>
    <div class="text">
      {{text}}
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import chroma from 'chroma-js'

export default defineComponent({
  name: 'ActionButton',
  props: {
    icon: String,
    text: String,
    textColor: String,
    buttonColor: String
  },
  data: function () {
    return {
      colorA: this.buttonColor,
      colorB: this.textColor,
      colorBLight: this.textColor === undefined
        ? this.textColor : chroma(this.textColor).brighten(),
      colorADark: this.buttonColor === undefined
        ? this.buttonColor : chroma(this.buttonColor).darken()
    }
  }
})
</script>

<style scoped lang="scss" vars="{ colorA, colorADark, colorB, colorBLight }">
@import '@/assets/scss/_brand';

div.button{
  border: 2px solid var(--colorA, $brandColor);
  background-color: var(--colorA, $brandColor);
  margin: 5px;
  color: var(--colorB, $brandLigthBackground);
  border-radius: 10px;
  // width: 100px;
  padding: 0px 10px;
  height: 40px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  font-weight: 600;
  font-size: 1.2em;
  box-shadow: 2px 2px 10px solid black;
  div.icon{
    margin-right: 5px;
  }
  div.text{
    user-select: none;
  }
}
div.button:hover{
  border-color: var(--colorADark, darken($brandColor, 25));
  color: var(--colorBLight, lighten($brandLigthBackground, 100));
  box-shadow: 0px 2px 2px rgba(#000,.2);
}
div.button:active{
  background-color: var(--colorADark, darken($brandColor, 25));
  color: var(--colorBLight, lighten($brandLigthBackground, 100));
}
</style>
