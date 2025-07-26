const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const user=ref([])
            const error=ref("")
            const UID=parseInt(window.location.pathname.split('/').pop());
            const scores=ref([])

            onMounted(async () => {
                try{
                    const response1=await axios.get(`/api/users/${UID}`);
                    user.value=response1.data;

                    const response2=await axios.get(`/api/users/scores/${UID}`)
                    scores.value=response2.data
                } catch(err) {
                    error.value=err
                }
            })

            const goBack = () => {
                    window.history.back();
                };

            return {user, error, scores, goBack}
        }
    }).mount("#app")