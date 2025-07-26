const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const users=ref([])
            const error=ref("")

            onMounted(async () => {
                try{
                    const response=await axios.get('/api/users');
                    users.value=response.data;
                } catch(err) {
                    error.value=err
                }
            })

            const goBack = () => {
                    window.history.back();
                };

            return {users, error, goBack}
        }
    }).mount("#app")