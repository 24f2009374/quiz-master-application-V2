const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const Chapters=ref([]);

            const error=ref("");
            const success=ref("");

            onMounted(async () => {
                try {
                    const response=await axios.get('/api/chapters');
                    Chapters.value=response.data
                } catch(err) {
                    error.value=err.response.data.error
                }
            });

            const goBack = () => {
                    window.history.back();
                };

            return { Chapters, error, success, goBack }
        }
    }).mount("#app")