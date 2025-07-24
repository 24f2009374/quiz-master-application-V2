const { ref, createApp, onMounted }=Vue;
    createApp({
        setup(){
            const user=ref("")
            const scores=ref("")

            onMounted(async () => {
                try {
                    const response=await axios.get('/api/users/me')
                    user.value=response.data

                    const response2=await axios.get(`/api/users/scores/${user.value.user_id}`)
                    scores.value=response2.data
                    console.log(scores.value)
                } catch(err) {
                    console.log(err)
                }
            })

            const triggerExport=async () => {
                try {
                    const response=await axios.get('/api/charts', {params:{ctx:"CSV"}})
                    alert("Export initiated - You will receive a download link shortly");
                } catch(err) {
                    console.log(err)
                    alert("Failed to trigger export");
                }
            }

            return {user, scores, triggerExport}
        }
    }).mount("#app")