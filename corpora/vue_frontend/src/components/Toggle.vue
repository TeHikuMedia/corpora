<template>
  <label class="switch">
    <input type="checkbox" v-model="checked" @change="changed()" >
    <span class="slider round"></span>
  </label>
</template>
<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({
  name: 'Toggle',
  props: {
    onColor: String,
    offColor: String
  },
  data: function () {
    return {
      onColorV: this.onColor !== undefined ? this.onColor : '#2196F3',
      offColorV: this.offColor !== undefined ? this.offColor : '#ccc',
      checked: false
    }
  },
  methods: {
    changed () {
      this.$emit('changed', this.checked)
    }
  }
})
</script>
<style scoped lang="scss" vars="{ onColorV, offColorV }">
label {
  margin-bottom: 0px;
}
/* The switch - the box around the slider */
.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 26px;
}

/* Hide default HTML checkbox */
.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

/* The slider */
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--offColorV, #ccc);
  -webkit-transition: .2s;
  transition: .2s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: .2s;
  transition: .2s;
}

input:checked + .slider {
  background-color: var(--onColorV, #2196F3);
}

input:focus + .slider {
  box-shadow: 0 0 1px var(--onColorV, #2196F3);
}

input:checked + .slider:before {
  -webkit-transform: translateX(18px);
  -ms-transform: translateX(18px);
  transform: translateX(18px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 26px;
}

.slider.round:before {
  border-radius: 50%;
}
</style>
