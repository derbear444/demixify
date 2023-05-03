<template>
  <div class="bg-gray-900 text-white rounded-md p-4">
    <h2 class="text-2xl font-bold mb-4">{{ songTitle.toUpperCase() }}</h2>
    <SeekBar @seek="updateSeek" :givenTime="currentTime" :songDuration="songDuration" />
    <br>
    <div class="flex items-center mb-4">
      <button @click="togglePlay" class="mr-4">
        <svg v-if="isPlaying" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M4.5 22h-3v-20h3v20zM19.5 22h-3v-20h3v20z"></path>
        </svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path d="M5 3v18l13-9L5 3z"></path>
        </svg>
      </button>
      <input type="range" min="-60" max="60" step="0.1" v-model="master_volume"
        @input="updateMasterVolume(master_volume)" />
      <div v-for="(track, index) in tracks" :key="index" class="mr-5">
        <label class="flex items-center cursor-pointer">
          <input type="checkbox" v-model="track.muted" class="sr-only" />
          <svg v-if="track.muted" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M17.25 9.75L19.5 12m0 0l2.25 2.25M19.5 12l2.25-2.25M19.5 12l-2.25 2.25m-10.5-6l4.72-4.72a.75.75 0 011.28.531V19.94a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.506-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.395C2.806 8.757 3.63 8.25 4.51 8.25H6.75z" />
          </svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
            stroke="currentColor" class="w-6 h-6">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z" />
          </svg>
          {{ track.name }}
        </label>
        <input type="range" min="-60" max="60" step="0.1" v-model="track.volume"
          @input="updateVolume(index, track.volume)" />
        <canvas ref="canvas"></canvas>
      </div>
    </div>
  </div>
</template>
  
<script>
import { defineComponent } from "vue";
import * as Tone from 'tone'

export default defineComponent({
  props: {
    songTitle: {
      type: String,
      required: true,
    },
    sources: {
      type: Array,
      required: true,
    },
    source_names: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      isPlaying: false,
      tracks: [],
      howls: [],
      pauseTime: 0,
      currentTime: 0,
      master_volume: 0,
      songDuration: 0,
    }
  },
  mounted() {
    // Run setup code
    this.setup();

    // Terrible way, but potentially the only way
    setInterval(() => {
      if (this.currentTime >= this.songDuration) {
        // Reset timer and stop player if its running
        Tone.Transport.stop();
        this.players.stopAll();
        this.isPlaying = false;
        this.currentTime = this.songDuration;
      } else {
        this.currentTime = Tone.Transport.seconds;
      }
    }, 1);
  },
  methods: {
    setup() {
      // Create players with specified options
      const options = {
        urls: this.sources.reduce((obj, src, i) => {
          obj[this.source_names[i]] = src;
          return obj;
        }, {}),
        onload: () => {
          console.log("Song loaded!")
        },
      }
      const ps = new Tone.Players(options).toDestination();
      // Set players' volume
      ps.volume.value = 1;

      this.players = ps;

      // Initialize tracks array
      this.tracks = this.source_names.map((name, index) => ({
        name: name,
        muted: false,
        volume: 1,
      }));

      // Create an analyser node that makes a waveform
      const wf = new Tone.Waveform(128).toDestination();

      // Connect with analyser as well so we can detect waveform
      this.players.connect(wf);

      this.waveform = wf;

      // create a Waveform object for each track
      // this.waveforms = this.tracks.map((track) => {
      //   const waveform = new Tone.Waveform(512);
      //   this.players.player(track.name).connect(waveform);
      //   return waveform;
      // });

      // // draw the waveforms on the canvas element
      // this.drawWaveforms();

      // Tone.start()
    },
    togglePlay() {
      if (this.currentTime >= this.songDuration) {
        this.currentTime = 0;
        this.pauseTime = 0;
      }

      if (this.players.loaded) {
        if (this.isPlaying) {
          this.pauseTime = Tone.Transport.seconds;
          Tone.Transport.pause()
          this.players.stopAll();
          this.isPlaying = false;
        } else {
          Tone.Transport.start()
          this.songDuration = this.players.player(this.source_names[0]).buffer.duration
          this.source_names.forEach((source) => {
            this.players.player(source).start(0, this.pauseTime);
          })
          this.isPlaying = true;
        }
      }
    },
    updateVolume(idx, value) {
      // Update specific player's volume
      this.players.player(this.source_names[idx]).volume.value = value;
    },
    updateMasterVolume(value) {
      this.players.volume.value = value;
    },
    updateSeek(position) {
      // Update all players' playback position
      this.source_names.forEach((source) => {
        this.players.player(source).seek(position);
      });
      Tone.Transport.seconds = position;
      this.pauseTime = position;
    },
    drawWaveforms() {
      const canvas = this.$refs.canvas;
      const ctx = canvas.getContext('2d');

      // clear the canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // set the canvas dimensions
      canvas.width = this.$el.clientWidth;
      canvas.height = 100 * this.tracks.length;

      // draw each waveform on the canvas
      this.waveforms.forEach((waveform, i) => {
        ctx.strokeStyle = `rgba(255, 255, 255, ${this.tracks[i].muted ? 0.5 : 1})`;
        ctx.beginPath();
        waveform.toCanvas(canvas, {
          stroke: true,
          strokeWidth: 2,
          color: ctx.strokeStyle,
          height: 100,
          offsetY: i * 100
        });
        ctx.closePath();
      });

      // schedule the next redraw
      requestAnimationFrame(this.drawWaveforms);
    },
  },
  watch: {
    tracks: {
      handler(tracks) {
        // Mute or unmute tracks
        tracks.forEach((track, index) => {
          const player = this.players.player(this.source_names[index]);
          player.mute = track.muted;
        });
      },
      deep: true,
    },
    sources: {
      handler() {
        // Zero everything back out
        this.currentTime = 0;
        this.pauseTime = 0;
        this.master_volume = 0;
        // Reset timer and stop player if its running
        Tone.Transport.stop();
        this.players.stopAll();
        this.isPlaying = false;
        // Rerun setup code
        this.setup();
      },
    },
  }
});
</script>