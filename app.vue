<template>
  <div :class="themeString" class="h-screen bg-themeBackground p-5">
    <div class="header flex justify-between items-center">
      <h1 class="text-themeText font-bold text-6xl tracking-tight leading-tight pb-3">Demixify</h1>
      <button class="bg-blue-500 hover:bg-blue-600 font-bold py-2 px-4 rounded" @click="toggleDarkMode">
        {{ darkMode ? 'Light Mode' : 'Dark Mode' }}
      </button>
    </div>
    <div :class="themeString" class="bg-gray-800 shadow-lg rounded-lg p-6">
      <form @submit.prevent="handleSendData">
        <div class="flex flex-wrap items-center space-x-4">
          <input class="flex-grow bg-gray-800 border border-gray-300 rounded-lg p-4 text-white" type="text" v-model="text"
            @keydown.enter="submit" placeholder="Enter song...">
          <input class="flex-grow-3 bg-gray-800 border border-gray-300 rounded-lg p-4 text-white" type="number"
            v-model="numSources" min="2" max="8" placeholder="Number of sources">
          <input class="flex-grow-3 bg-gray-800 border border-gray-300 rounded-lg p-4 text-white" type="number"
            v-model="numIterations" min="100" max="1000" placeholder="Number of iterations">
          <input class="flex-grow-3 bg-gray-800 border border-gray-300 rounded-lg p-4 text-white" type="number"
            v-model="duration" placeholder="Duration in seconds">
          <div class="flex items-center space-x-2">
            <input type="checkbox" class="h-6 w-6 text-gray-300 border-gray-300 rounded focus:ring-0"
              v-model="regenIfFound">
            <label for="regenIfFound" class="text-white">Regen if Found?</label>
          </div>
          <button class="bg-blue-500 hover:bg-blue-600 font-bold py-2 px-4 rounded" type="submit">Send Data</button>
        </div>
        <div v-if="loading" class="flex items-center space-x-2 mt-4">
          <div class="animate-pulse w-4 h-4 bg-blue-500 rounded-full"></div>
          <div class="text-white">Loading audio...</div>
        </div>
      </form>
      <MultitrackAudioPlayer v-if="showPlayer" :songTitle="songName" :sources="audios" :source_names="names" />
      <img v-if="showPlayer" :src=graphLink class="my-4" @load="toggleImageLoading"/>
      <div v-if="showPlayer && !imageLoad" class="w-full h-96 flex justify-center items-center">
        <div class="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
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
      songName: "",
      numSources: 6,
      numIterations: 500,
      duration: 20,
      regenIfFound: false,
      graphLink: "",
      imageLoad: false,
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

      if (check && !this.regenIfFound) {
        await this.sendLimitedData(this.text).then((data) => {
          if (typeof data != "string") {
            this.names = data.map((source) => source.name);
            this.audios = data.map((source) => source.audio);
          }
        }).catch((e) => {
          console.log(e);
        });
      }
      else {
        await this.sendData(this.text).then((data) => {
          if (typeof data != "string") {
            this.names = data.map((source) => source.name);
            this.audios = data.map((source) => source.audio);
          }
        }).catch((e) => {
          console.log(e);
        });
      }
      this.loading = false;
    },
    async sendData(song_name) {
      console.log("Attempting to load brand new song...")

      const songNameData = await useFetch(
        `http://152.10.212.186:5000/api/search?song_name=${song_name}`,
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
      const songInfo = JSON.parse(songNameData.data.value);

      const songID = songInfo[0];
      const searchedName = songInfo[1]; 
      this.songName = searchedName;

      console.log(`Song name: ${searchedName}`);
      const { data, pending, error, refresh } = await useFetch(
        `http://152.10.212.186:5000/api/full?song_name=${searchedName}&song_id=${songID}&num_sources=${this.numSources}&num_iterations=${this.numIterations}&split_duration=${this.duration}&regen=${this.regenIfFound}`,
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
      this.setImageLink(searchedName);
      return sourcesArr;
    },
    async sendLimitedData(song_name) {
      console.log("Attempting to use combo already in system...")

      const songNameData = await useFetch(
        `http://152.10.212.186:5000/api/search?song_name=${song_name}`,
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
      const songInfo = JSON.parse(songNameData.data.value);

      const searchedName = songInfo[1]; 
      this.songName = searchedName;

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
      this.setImageLink(searchedName);
      return sourcesArr;
    },
    setImageLink(song_name) {
      this.graphLink = `http://152.10.212.186:5000/api/visualize?combo_name=${song_name}.wav`
    },
    toggleImageLoading() {
      console.log("Image finished loading!");
      this.imageLoad = !this.imageLoad;
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