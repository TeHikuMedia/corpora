/* eslint-disable @typescript-eslint/camelcase */
<template>
  <div class="viewContainer">
    <div class='sidepanel'>
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
        <a class="follow-up"
           v-on:click="qc_toggle('follow_up')"
           v-bind:class="{ checked: qc.follow_up , disabled: buttonsDisabled}">
          <i class="fas fa-reply fa-fw"></i>
          <span >Follow Up</span>
        </a>
        <a class="noise"
           v-on:click="qc_toggle('noise')"
           v-bind:class="{ checked: qc.noise , disabled: buttonsDisabled}">
          <i class="fas fa-bullhorn fa-fw"></i>
          <span>Noise</span>
        </a>
        <a class="approve"
           v-on:click="qc_toggle('approve')"
           v-bind:class="{ disabled: buttonsDisabled }">
          <font-awesome-icon icon="check-circle" fixed-width />
          <span>Approve</span>
        </a>
        <a class="good"
           v-on:click="qc_toggle('good')"
           v-bind:class="{ disabled: buttonsDisabled }">
          <font-awesome-icon icon="check" fixed-width />
          <span>Ka Tika</span>
        </a>
        <a class="bad"
           v-on:click="qc_toggle('bad')"
           v-bind:class="{ disabled: buttonsDisabled }">
          <font-awesome-icon icon="times" fixed-width />
          <span>Kia Kaha</span>
        </a>
        <a class="delete"
           v-on:click="qc_toggle('delete')"
           v-bind:class="{ disabled: buttonsDisabled}">
          <font-awesome-icon icon="trash" fixed-width />
          <span>Delete</span>
        </a>
      </div>
      <div class="slider">
        <div class="sliderGroup">
          <div class="rangeLabel">Incorrect</div>
          <input type="range" min="0" max="100" class="slider" id="myRange" v-model="sliderValue">
          <div class="rangeLabel">Correct</div>
        </div>
        <div class="sliderLabel">
          Move the slider based on how good you think the speaker's pronunciation is.
        </div>
        <div class="notes">
          <textarea placeholder="Notes" v-model="qc.notes"></textarea>
        </div>
      </div>
    </div>
    <div class="pronunciation">
      <div class="sentence">
        <div class="word" v-for="(charObject,i) in charatersObject" :key="i"
         :style="{width: 40*charObject.word.length+'px'}">
          <div class="character" v-for="(c, j) in charObject.chars" :key="i+' '+j"
           :style="{backgroundColor: c.vote ? '#ef476f' : '#64dfdf'}"
           v-on:click="c.vote = c.vote ? false : true; updateSlider()">
            <div class="char">{{c.character}}</div>
            <div class="index">{{c.index}}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { getRandomRecording, postRecordingQC, getMyself } from '../api'
import Toggle from '@/components/Toggle.vue' // @ is an alias to /src

import {
  RecordingObject,
  CharVote,
  CharStructure,
  PronunciationJSON,
  PostRecordingQualityControl
} from '@/api/interfaces'

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
      charatersObject: [] as Array<CharStructure>,
      audioElm: {} as HTMLAudioElement,
      playing: false,
      autoPlay: false,
      sliderValue: 50,
      buttonsDisabled: true,
      person: 0,
      qc: {} as PostRecordingQualityControl
    }
  },
  mounted: function () {
    this.audioElm = this.$refs.audio as HTMLAudioElement
    this.audioElm.onended = this.audioEnded
    getMyself().then((result) => {
      this.person = result
      this.qc.person = result
    })
    this.nextRecording()

    const setVh = () => {
      const vh = window.innerHeight * 0.01
      console.log('resize')
      document.documentElement.style.setProperty('--vh', `${vh}px`)
    }

    window.addEventListener('load', setVh)
    window.addEventListener('resize', setVh)
  },
  computed: {
    pronunciationJSON (): PronunciationJSON {
      return {
        ratingSlider: this.sliderValue / 100,
        ratingComputed: this.getComputedVote(),
        characterVotes: this.charatersObject
      }
    },
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
    updateSlider () {
      this.sliderValue = Math.round(100 * this.getComputedVote())
    },
    getComputedVote (): number {
      let numChars = 0
      let numBad = 0
      this.charatersObject.forEach((charObj) => {
        // console.log('test')
        charObj.chars.forEach((char) => {
          numChars += 1
          if (char.vote) {
            numBad += 1
          }
        })
      })
      if (numChars === 0) {
        return 0
      } else {
        return 1 - numBad / numChars
      }
    },
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
    audioEnded () {
      this.playing = false
      this.buttonsDisabled = false
    },
    nextRecording () {
      this.reset()
      getRandomRecording()
        .then((response) => {
          this.recording = response.data.results[0]
          this.qc.recording = this.recording.id
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
    },
    reset () {
      if (this.playing) {
        this.audioElm.pause()
        this.playing = false
      }
      this.buttonsDisabled = true
      this.qc = {} as PostRecordingQualityControl
      if (this.person !== 0) {
        this.qc.person = this.person
      }
      this.sliderValue = 50
    },
    qc_toggle (field: string) {
      if (!this.buttonsDisabled) {
        switch (field) {
          case 'follow_up':
            this.qc.follow_up = !this.qc.follow_up
            break
          case 'noise':
            this.qc.noise = !this.qc.noise
            break
          case 'delete':
            this.qc.trash = true
            this.post()
            break
          case 'good':
            this.qc.good = 1
            this.post()
            break
          case 'bad':
            this.qc.bad = 1
            this.post()
            break
          case 'approve':
            this.qc.approved = true
            this.post()
            break
          default:
            break
        }
      }
    },
    post () {
      this.qc.pronunciation = this.pronunciationJSON
      postRecordingQC(this.qc)
      this.nextRecording()
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
  height: calc(var(--vh, 1vh) * 100);
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
  top: 50px;
  width: 100%;
  max-height: 250px;
  div.audio{
    margin-top: 0px;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  }
  div.slider{
    font-size: 1.1em;
    div{
      display: flex;
      justify-content: center;
      align-content: center;
      align-items: center;
      div{
        padding: 0px 15px;
        font-weight: 700;
        font-size: 0.9em;
      }
      input, textarea{
        width: 100%;
        max-width: 500px;
        -webkit-appearance: none;
        appearance: none;
        height: 10px;
        border-radius: 4px;
        background: #d3d3d3;
        outline: none;
      }
      input::-webkit-slider-thumb {
        -webkit-appearance: none;
        appearance: none;
        width: 20px;
        height: 20px;
        border: 0px;
        border-radius: 20px;
        background: $brandColor;
        cursor: pointer;
      }

      input::-moz-range-thumb {
        width: 20px;
        height: 20px;
        border: 0px;
        border-radius: 20px;
        background: $brandColor;
        cursor: pointer;
      }
      textarea{
        height: 34px;
        border: 0px;
        margin-top: 10px;
        max-width: 600px;
        padding: 4px 8px;
      }
    }
    div.sliderLabel{
      font-style: italic;
      font-size: 0.8em;
    }
    div.notes{
      font-size: 0.9em;
      padding: 0px 20px;
    }
    width: 100%;
    padding: 0px 0px;
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
  margin-bottom: 10px;
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
      max-height: 250px;
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
      width: 96px;
      border-width: 1px;
      font-size: .8em !important;
    }
  }
  .play{
    font-size: 3em;
  }
  div.sliderLabel{
    font-size: 0.5em !important;
  }
  div.slider{
    div{
      font-size: 0.7em;
    }
  }
}
</style>
