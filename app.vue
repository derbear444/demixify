<template>
  <div :class="themeString" class="h-screen bg-themeBackground p-5">
    <div class="header flex justify-between items-center">
      <h1 class="text-themeText font-bold text-6xl tracking-tight leading-tight pb-3">Deximify</h1>
      <button class="bg-blue-500 hover:bg-blue-600 font-bold py-2 px-4 rounded" @click="toggleDarkMode">
        {{ darkMode ? 'Light Mode' : 'Dark Mode' }}
      </button>
    </div>
    <div :class="themeString" class="bg-gray-800 shadow-lg rounded-lg p-6">
      <form @submit.prevent="handleSendData">
        <div class="flex flex-col space-y-4">
          <input class="bg-gray-800 border border-gray-300 rounded-lg p-4 text-white" type="text" v-model="text"
            @keydown.enter="submit" placeholder="Enter text here">
          <button class="bg-blue-500 hover:bg-blue-600 font-bold py-2 px-4 rounded" type="submit">Send
            Data</button>
          <div v-if="loading" class="flex items-center space-x-2">
            <div class="animate-pulse w-4 h-4 bg-blue-500 rounded-full"></div>
            <div class="text-white">Loading audio...</div>
          </div>
          <MultitrackAudioPlayer v-if="showPlayer" :songTitle="text" :sources="audios" :source_names="names" />
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import MultitrackAudioPlayer from "./components/MultitrackAudioPlayer.vue";

export default {
  data() {
    return {
      text: '',
      names: [],
      audios: [],
      loading: false,
      darkMode: true,
    };
  },
  methods: {
    async handleSendData() {
      this.loading = true;
      const { data, pending, error, refresh } = await useFetch(
        `http://152.10.212.186:5000/api/combos`,
        {
          onRequest({ request, options }) {
            // Set the request headers
            options.headers = options.headers || {};
            options.headers.authorization = "...";
          },
          onRequestError({ request, options, error }) {
            // Handle the request errors
            return error
          },
          onResponse({ request, response, options }) {
            // Process the response data
            return response._data;
          },
          onResponseError({ request, response, options }) {
            // Handle the response errors
          },
        }
      );
      const combos = JSON.parse(data.value);
      const comboString = `${this.text}.wav-combined.npy`;
      const check = combos.includes(comboString);

      if (check) {
        await this.sendLimitedData(this.text).then((data) => {
          if (typeof data != "string") {
            this.names = data.map((source) => source.name);
            this.audios = data.map((source) => source.audio);
          }
        });
      }
      else {
        await this.sendData(this.text).then((data) => {
          if (typeof data != "string") {
            this.names = data.map((source) => source.name);
            this.audios = data.map((source) => source.audio);
          }
        });
      }
      this.loading = false;
    },
    async sendData(song_name) {
      console.log("Attempting to load brand new song...")
      console.log(`Song name: ${song_name}`)
      const { data, pending, error, refresh } = await useFetch(
        `http://152.10.212.186:5000/api/full?song_name=${song_name}.wav`,
        {
          onRequest({ request, options }) {
            // Set the request headers
            options.headers = options.headers || {};
            options.headers.authorization = "...";
          },
          onRequestError({ request, options, error }) {
            // Handle the request errors
            return error
          },
          onResponse({ request, response, options }) {
            // Process the response data
            return response._data;
          },
          onResponseError({ request, response, options }) {
            // Handle the response errors
          },
        }
      );
      const sourcesArr = JSON.parse(data.value);
      return sourcesArr;
    },
    async sendLimitedData(song_name) {
      console.log("Attempting to use combo already in system...")
      console.log(`Song name: ${song_name}`)
      const { data, pending, error, refresh } = await useFetch(
        `http://152.10.212.186:5000/api/embeded_audio?combo_name=${song_name}.wav`,
        {
          onRequest({ request, options }) {
            // Set the request headers
            options.headers = options.headers || {};
            options.headers.authorization = "...";
          },
          onRequestError({ request, options, error }) {
            // Handle the request errors
            return error
          },
          onResponse({ request, response, options }) {
            // Process the response data
            return response._data;
          },
          onResponseError({ request, response, options }) {
            // Handle the response errors
          },
        }
      );
      const sourcesArr = JSON.parse(data.value);
      return sourcesArr;
    },
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
    },
  },
  computed: {
    showPlayer() {
      return this.names.length !== 0
    },
    themeString() {
      return this.darkMode ? "theme-dark" : "theme-light"
    },
  },
};
</script> 