<script type='text/x-template' id="test">
  <div  v-bind:style="styleObject">

      <div v-if="recording != null" class="sentence">
      <div class="char" v-for="character in recording.sentence_text" >
        <div class="char-wrapper">
            <span class="char">${character}</span>
        </div>
      </div>
      </div>    


  </div>
</script>

<script type="text/javascript">
Vue.component('v-test', {
  delimiters: ['${', '}'],
  props: ['message'],
  template: '#test',
  data() {
    return {
      test: 'hellp',
      styleObject: {
        color: 'red',
      },      
      recordings: [],
      recording: null,
    }
  },
  methods: {
    getRandomRecording: function(){
      fetch('https://corporalocal.nz/api/listen/',{
        method: 'get',
        // mode: 'cors',
        // credentials: 'same-origin',
        headers: {
          // "X-CSRFToken": csrftoken,
          "Authorization": '${token}',
        },
      })
      .then(response => response.json())
      .then((data)=>{
        console.log(data)
        console.log(this.test)
        this.recordings = data.results
        this.recording = this.recordings.pop()
        console.log(this.recording)
        console.log(this.recording.text)
      })

    }
  },
  mounted: function(){
    this.getRandomRecording()
  }
})

new Vue({
  el: '#vue-app',
})
</script>

<style type="text/css" scoped>
  div.sentence{
    display: inline-flex;
  }
  div.char{
    /*line-height: 20px;*/
  }
  div.char-wrapper{
    width: 20px;
    display: inline-block;
    text-align: center;
  }
</style>