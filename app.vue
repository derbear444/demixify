<template>
  <div>
    <NuxtLayout>
      <textarea v-model="text"></textarea>
      <button @click="handleSendData">Send Data</button>
      <MultitrackAudioPlayer v-if="names.length != 0" :songTitle="text" :sources="audios" :source_names="names" />
    </NuxtLayout>
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
    };
  },
  methods: {
    async handleSendData() {
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
        this.sendLimitedData(this.text).then((data) => {
          console.log(data)
          if (typeof data != "string") {
            this.names = data.map((source) => source.name);
            this.audios = data.map((source) => source.audio);
          }
        });
      }
      else {
        await this.sendData(this.text).then((data) => {
          console.log(data)
          if (typeof data != "string") {
            this.names = data.map((source) => source.name);
            this.audios = data.map((source) => source.audio);
          }
        });
      }
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
  },
};
</script> 