<template>
    <div>
        <textarea v-model="text"></textarea>
        <button @click="sendData">Send Data</button>
    </div>
</template>
  
<script>
export default {
    data() {
        return {
            text: '',
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
            const names = sourcesArr.map((source) => source.name);
            const audios = sourcesArr.map((source) => source.audio);

            const params = {
                names: names,
                audios: audios,
            }

            return params;
        },
    },
};
</script>  