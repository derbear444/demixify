<template>
  <div>
    <NuxtLayout>
      <MultitrackAudioPlayer
        songTitle="So Much for Stardust"
        :sources="audios"
        :source_names="names"
      />
    </NuxtLayout>
  </div>
</template>

<script setup>
import MultitrackAudioPlayer from "./components/MultitrackAudioPlayer.vue";

const { data, pending, error, refresh } = await useFetch(
  "http://152.10.212.186:5000/api/embeded_audio?combo_name=so-much-for-stardust.wav",
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
const names = sourcesArr.map((source) => source.name);
const audios = sourcesArr.map((source) => source.audio);
</script>