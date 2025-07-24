const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const QuizObj=ref({});

            const error=ref("");
            const success=ref("");

            const quiz_id=parseInt(window.location.pathname.split('/').at(-1));

            onMounted(async () => {
                try {
                    const response=await axios.get(`/api/prepare/${quiz_id}`);
                    QuizObj.value=response.data;
                    
                } catch(err) {
                    error.value=err.response.data.error;
                }
            });

            return { QuizObj, error, success }
        }
    }).mount("#app")