// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    runtimeConfig: {
        title: 'Demixify',
        // Public keys that are exposed to the client
        public: {
            apiBase: `${process.env.NUXT_PUBLIC_API_BASE_URL}/api`
        },
    },
    modules: [    
        '@nuxtjs/tailwindcss',    
        '@nuxt/image-edge',  
    ],
})
