const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const Quizzes=ref([]);

            const error=ref("");
            const success=ref("");

            onMounted(async () => {
                try {
                    const response=await axios.get('/api/quizzes');
                    Quizzes.value=response.data
                } catch(err) {
                    error.value=err.response.data.error
                }
            });

            return { Quizzes, error, success }
        }
    }).mount("#app")