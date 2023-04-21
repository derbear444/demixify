<template>
  <div class="bg-gray-900 text-white rounded-md p-4">
    <h2 class="text-2xl font-bold mb-4">{{ songTitle }}</h2>
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
      });
    });

    // Initialize tracks array
    this.tracks = this.source_names.map((name, index) => ({
      name: name,
      muted: false,
    }));
  },
  methods: {
    togglePlay() {
      if (this.isPlaying) {
        this.howls.forEach((howl) => howl.pause());
      } else {
        this.howls.forEach((howl) => howl.play());
      }
      this.isPlaying = !this.isPlaying;
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