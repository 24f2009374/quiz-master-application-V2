const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const error=ref("")
            const success=ref("")
            const quizID=parseInt(window.location.pathname.split('/').pop());
            const scores=ref([])

            onMounted(async () => {
                try{
                    const response=await axios.get(`/api/scores/${quizID}`);
                    scores.value=response.data

                } catch(err) {
                    error.value=err
                }
            })

            return { error, success, scores }
        }
    }).mount("#app")