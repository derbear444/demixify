<template>
  <div class="bg-gray-900 text-white rounded-md p-4">
    <h2 class="text-2xl font-bold mb-4">{{ songTitle }}</h2>
    <div class="flex items-center mb-4">
      <button @click="togglePlay" class="mr-4">
        <svg v-if="isPlaying" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M5 3v18l13-9L5 3z"></path>
        </svg>
        <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M4.5 22h-3v-20h3v20zM19.5 22h-3v-20h3v20z"></path>
        </svg>
      </button>
      <div v-for="(track, index) in tracks" :key="index" class="mr-4">
        <label class="flex items-center cursor-pointer">
          <input type="checkbox" v-model="track.muted" class="sr-only" />
          <span class="bg-gray-800 rounded-full w-6 h-6 flex items-center justify-center mr-2">
            {{ index + 1 }}
          </span>
          {{ track.name }}
        </label>
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
  },
  data() {
    return {
      isPlaying: false,
      tracks: [],
      howl: null,
    };
  },
  mounted() {
    // Create Howl instance
    this.howl = new Howl({
      src: this.sources,
      html5: true,
      preload: true,
      onload: () => {
        // Initialize tracks array
        this.tracks = this.howl._sounds.map((sound, index) => ({
          name: `Track ${index + 1}`,
          muted: false,
        }));
      },
    });
  },
  methods: {
    togglePlay() {
      if (this.isPlaying) {
        this.howl.pause();
      } else {
        this.howl.play();
      }
      this.isPlaying = !this.isPlaying;
    },
  },
  watch: {
    tracks: {
      handler(tracks) {
        // Mute or unmute tracks
        tracks.forEach((track, index) => {
          const sound = this.howl._sounds[index];
          sound.mute(track.muted);
        });
      },
      deep: true,
    },
  },
});
</script>
  