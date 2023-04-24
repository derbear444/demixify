<template>
  <div>
    <NuxtLayout>
      <textarea v-model="text"></textarea>
      <button @click="sendData">Send Data</button>
      <MultitrackAudioPlayer
        v-if="names.length != 0"
        songTitle="So Much for Stardust"
        :sources="audios"
        :source_names="names"
      />
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
    async sendData() {
      const { data, pending, error, refresh } = await useFetch(
        `http://152.10.212.186:5000/api/embeded_audio?combo_name=${this.text}`,
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
      const sourcesArr = JSON.parse(data.value)

      this.names = sourcesArr.map((source) => source.name);
      this.audios = sourcesArr.map((source) => source.audio);
    },
  },
};
</script> 