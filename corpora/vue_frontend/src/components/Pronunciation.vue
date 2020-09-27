/* eslint-disable @typescript-eslint/camelcase */
<template>
  <div class="pronunciation">
    <div>{{recording}}</div>
    <div class="sentence">
      <div class="word" v-for="(charObject,i) in charatersObject" :key="i"
       :style="{width: 40*charObject.word.length+'px'}">
        <div class="character" v-for="(c, j) in charObject.chars" :key="i+' '+j"
         :style="{backgroundColor: c.vote ? '#ef476f' : '#64dfdf'}"
         v-on:click="c.vote = c.vote ? false : true">
          <div class="char">{{c.character}}</div>
          <div class="index">{{c.index}}</div>
        </div>
      </div>
    </div>
    <div class="audio">
      <button :class="{active: autoPlay}" v-on:click="autoPlay = autoPlay ? false : true">Auto Play</button>
      <font-awesome-icon icon="play-circle" size="6x" fixed-width class="play"
      v-on:click="toggleAudio();" v-if="!playing"/>
      <font-awesome-icon icon="pause-circle" size="6x" fixed-width class="play"
      v-on:click="toggleAudio();" v-if="playing"/>
      <button>Submit</button>
      <audio :src="recording.audio_file_url" ref="audio"></audio>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { getRandomRecording } from '../api'

interface RecordingObject {
  sentence_text: string;
  audio_file_url: string;
}

interface CharVote {
  character: string;
  vote: boolean;
  index: number;
  wordIndex: number;
}

interface CharStructure {
  word: string;
  chars: Array<CharVote>;
}

export default defineComponent({
  name: 'Pronunciation',
  data: function () {
    return {
      foo: 'bar',
      recording: {
        sentence_text: 'foo',
        audio_file_url: 'bar'
      } as RecordingObject,
      words: ['test', 'ing'],
      charatersObject: {} as Array<CharStructure>,
      audioElm: {} as HTMLAudioElement,
      playing: false,
      autoPlay: false
    }
  },
  mounted: function () {
    this.audioElm = this.$refs.audio as HTMLAudioElement

    this.audioElm.onended = this.audioEnded

    console.log('mounted')
    const result = getRandomRecording()
      .then((response) => {
        this.recording = response.data.results[0]
        this.charatersObject = this.getCharacters
      })
      .catch((error) => {
        console.log(error)
      })
      .then(() => {
        console.log('completed')
      })
    console.log(result)
  },
  computed: {
    getCharacters (): Array<CharStructure> {
      const words = this.recording.sentence_text.split(' ')
      const data: Array<CharStructure> = []
      let count = 0
      words.forEach((value, index) => {
        const chars: Array<CharVote> = []
        for (let j = 0; j < value.length; j++) {
          const char = value[j]
          const c: CharVote = {
            character: char,
            vote: false,
            index: count,
            wordIndex: index
          }
          chars.push(c)
          count += 1
        }
        if (value !== '') {
          data.push({
            word: value,
            chars: chars
          })
        }
        count += 1
      })
      return data
    }
  },
  methods: {
    toggleAudio () {
      const a = this.$refs.audio as HTMLAudioElement
      if (a.paused) {
        a.play()
        this.playing = true
      } else {
        a.pause()
        this.playing = false
      }
    },
    audioEnded () {
      this.playing = false
    }
  }
})
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
div.pronunciation{
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 30px;
  div.sentence{
    padding: 30px;
    // max-width: 500px;
    align-items: center;
    justify-content: center;
    align-content: flex-start;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    div.word{
      display: flex;
      div.character{
        cursor: pointer;
        div.char{
          font-family: monospace;
          font-size: 32px;
          font-weight: 600;
          margin: 5px;
          user-select: none;
        }
        div.index{
          margin-top: -5px;
          font-size: 10px;
        }
        display: inline-block;
        width: 40px;
        height: 50px;
        border: 1px solid black;
        border-right: 0px;
        // overflow: hidden;
      }
      div.character:last-of-type{
        border-right: 1px solid black;
      }
      margin-right: 40px;
      margin-top: 40px;
    }
  }
  div.audio{
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
}
.play{
  color: #dc2250;
}
.play:active{
  color: darken(#dc2250, 10);
}

button{
  border: 2px solid #000;
  border-radius: 20px;
  background-color: #fff;
  font-weight: 600;
  color: #000;
  height: 40px;
}
button.active{
  background-color: #000;
  color: white;

}

</style>
