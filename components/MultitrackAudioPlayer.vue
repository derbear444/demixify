<template>
  <div class="bg-gray-900 text-white rounded-md p-4">
    <h2 class="text-2xl font-bold mb-4">{{ songTitle }}</h2>
    <SeekBar @seek="updateSeek" />
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
      <div v-for="(track, index) in tracks" :key="index" class="mr-4">
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
        <input type="range" min="0" max="1" step="0.01" v-model="track.volume"
          @input="updateVolume(index, track.volume)" />
      </div>
    </div>
  </div>
</template>
  
<script>
import { defineComponent } from "vue";
import { Howl } from "howler";

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
    };
  },
  mounted() {
    // Create Howl instances
    this.howls = this.sources.map((source) => {
      return new Howl({
        src: source,
        html5: true,
        preload: true,
        volume: 0.5,
      });
    });

    // Initialize tracks array
    this.tracks = this.source_names.map((name, index) => ({
      name: name,
      muted: false,
      volume: 0.5,
    }));
  },
  methods: {
    togglePlay() {
      if (this.isPlaying) {
        this.howls.forEach((howl) => {
          howl.pause();
          this.isPlaying = false;
          howl.off('play');
          howl.off('end');
        });
      } else {
        let counter = 0;
        const total = this.howls.length;
        this.howls.forEach((howl) => {
          howl.play();
          howl.on('play', () => {
            counter++;
            if (counter === total) {
              this.isPlaying = true;
            }
          });
          howl.on('end', () => {
            if (this.isPlaying) {
              this.togglePlay();
            }
          });
        });
      }
    },
    updateVolume(idx, value) {
      this.howls[idx].volume(value);
    },
    updateSeek(position) {
      this.howls.forEach((howl) => {
        howl.seek(howl.duration() * (position / 100));
      });
    },
  },
  watch: {
    tracks: {
      handler(tracks) {
        // Mute or unmute tracks
        tracks.forEach((track, index) => {
          const howl = this.howls[index];
          howl.mute(track.muted);
        });
      },
      deep: true,
    },
  },
});
</script>