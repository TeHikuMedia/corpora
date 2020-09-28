/* eslint-disable @typescript-eslint/camelcase */
<template>
  <div class="viewContainer">
    <div class="pronunciation">
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
    </div>
    <div class='sidepanel'>
      <div class="slider">
        <input type="range" min="1" max="100" value="0" class="slider" id="myRange">
      </div>
      <div class="audio actions">
        <div class="autoPlay">
          <div><Toggle ref="toggleAutoPlay"  onColor="#dc2250"
            v-on:changed="toggleAutoPlay($event)"/></div>
          <span>Auto Play</span>
        </div>
        <font-awesome-icon icon="play-circle"  fixed-width class="play"
        v-on:click="toggleAudio();" v-if="!playing"/>
        <font-awesome-icon icon="pause-circle"  fixed-width class="play"
        v-on:click="toggleAudio();" v-if="playing"/>
        <a href="javascript:void(0)" id="next disabled" class="next"
         v-on:click="nextRecording();">
          <i class="fas fa-step-forward fw"></i>
          <span>Skip</span>
        </a>
        <audio :src="recording.audio_file_url" ref="audio"></audio>
      </div>
      <div class="actions">
        <a class="follow-up disabled toggle-after-playback" data-key="follow_up">
          <i class="fas fa-reply fa-fw"></i>
          <span>Follow Up</span>
        </a>
        <a class="noise disabled toggle-after-playback" data-key="noise">
          <i class="fas fa-bullhorn fa-fw"></i>
          <span>Noise</span>
        </a>
        <a class="delete disabled toggle-after-playback" data-key="trash">
          <font-awesome-icon icon="trash" fixed-width />
          <span>Delete</span>
        </a>
        <a class="approve disabled toggle-after-playback">
          <font-awesome-icon icon="check-circle" fixed-width />
          <span>Approve</span>
        </a>
        <a class="good disabled toggle-after-playback">
          <font-awesome-icon icon="check" fixed-width />
          <span>Ka Tika</span>
        </a>
        <a class="bad disabled toggle-after-playback">
          <font-awesome-icon icon="times" fixed-width />
          <span>Kia Kaha</span>
        </a>

      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { getRandomRecording } from '../api'
import Toggle from '@/components/Toggle.vue' // @ is an alias to /src

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
  components: {
    Toggle
  },
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
    this.nextRecording()
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
    toggleAutoPlay (event: boolean) {
      this.autoPlay = event
      if (this.autoPlay) {
        this.audioElm.oncanplay = () => {
          this.toggleAudio()
        }
      } else {
        this.audioElm.oncanplay = null
      }
    },
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
    toggleButtons (state: string) {
      const buttons = document.getElementsByClassName('toggle-after-playback') as HTMLCollectionOf<Element>
      console.log(buttons)
      for (let i = 0; i < buttons.length; i++) {
        if (state === 'enabled') {
          buttons[i].classList.remove('disabled')
        } else if (state === 'disabled') {
          buttons[i].classList.add('disabled')
        } else {
          // code...
        }
      }
    },
    audioEnded () {
      this.playing = false
      this.toggleButtons('enabled')
    },
    nextRecording () {
      if (this.playing) {
        this.audioElm.pause()
        this.playing = false
      }
      this.toggleButtons('disabled')
      const result = getRandomRecording()
        .then((response) => {
          this.recording = response.data.results[0]
          this.charatersObject = this.getCharacters
          if (this.autoPlay) {
            this.audioElm.oncanplay = () => {
              this.toggleAudio()
            }
          }
        })
        .catch((error) => {
          console.log(error)
        })
        .then(() => {
          console.log('completed')
          console.log(this.autoPlay)
        })
    }
  }
})
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
@import '@/assets/scss/_actionButtons';
@import '@/assets/scss/_brand';

div.viewContainer {
  margin: 0px;
  padding: 0px;
  display: flex;
  justify-content: center;
  width: 100%;
  flex-direction: column;
  align-items: center;
  overflow-y: hidden;
  height: 100vh;
}
div.pronunciation{
  flex-grow: 2;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 15px;
  margin-top: 40px;
  width: 100%;
  overflow-y: auto;
  div.sentence{
    height: 100%;
    padding: 0px;
    max-width: 100%;
    align-items: center;
    justify-content: center;
    align-content: flex-start;
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    div.word{
      display: flex;
      flex-wrap: wrap;
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
      margin-right: 30px;
      margin-top: 30px;
    }
  }

}
div.sidepanel{
  flex-grow: 1;
  background-color: rgba($brandLigthBackground, 0.8);
  position: sticky;
  bottom: 0;
  width: 100%;
  max-height: 200px;
  div.audio{
    margin-top: 0px;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  div.slider{
    padding-top: 15px;
  }
}
.play{
  font-size: 4em;
  color: $brandColor;
  background-color: rgba($brandLigthBackground, 0);
}
.play:active{
  color: darken($brandColor, 10);
}

div.actions{
  margin: 0px;
  margin-bottom: 15px;
  a{
    background-color: lighten($brandLigthBackground, 6);
    font-size: 1.0em;
    width: 130px;
    cursor: pointer;
    font-weight: 500;
  }
  span{
    margin-left: 5px;
  }
}
div.audio.actions{
  a{
    background-color: rgba(white,0);
    width: 70px;
    margin: 0px;
    padding: 5px 0px;
    border: 0px;
  }
  a:first-of-type{
    span{
      margin-left: 0px;
    }
  }
}
div.autoPlay{
  width: 70px;
  display: flex;
  flex-direction: column;
  align-items: center;
  span{
    font-size: 12px;
    color: darken($brandColor, 100);
    padding-right: 5px;
  }
}

@media only screen and (max-width: 900px) {
  div.viewContainer{
    width: 100%;
    max-width: 100%;
    flex-direction: column;
    align-items: center;
  }
  div.actions{
    margin-bottom: 10px;
    a{
      width: 130px;
      font-size: 1em !important;
    }
  }
  .play{
    font-size: 4em;
  }
  div.pronunciation{
    flex-wrap: wrap;
    width: 100%;
    padding: 10px;
    div.sentence{
      div.word{
        margin-top: 20px;
        margin-right: 15px;
        div.character{
          height: 50px;
          div.char{
            font-size: 22px;
          }
          div.index{
            font-size: 6pt;
            margin-top: -10px;
          }
        }
      }
    }
    div.audio{
      margin-top: 5px;
    }
    div.sidepanel{
      max-height: 240px;
    }
  }
}
@media only screen and (max-width: 400px) {
  div.pronunciation{
    flex-wrap: wrap;
    width: 100%;
    padding: 10px;
    overflow-y: auto;
    div.sentence{
      div.word{
        margin-top: 15px;
        margin-right: 15px;
        div.character{
          height: 40px;
          div.char{
            font-size: 16px;
          }
          div.index{
            font-size: 5pt;
            margin-top: -6px;
          }
        }
      }
    }
    div.audio{
      margin-top: 5px;
    }
  }
  div.sidepanel{
    max-height: 234px;
  }
  div.actions{
    margin-bottom: 10px;
    a{
      width: 100px;
      font-size: .8em !important;
    }
  }
  .play{
    font-size: 3em;
  }
}
</style>
