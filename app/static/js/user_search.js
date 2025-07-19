const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const results=ref({});
            const quizzes=ref([]);
            const error=ref("");
            const success=ref("");
            const user=ref("");

            onMounted(async () =>{
                const URLParam=new URLSearchParams(window.location.search);
                const query=URLParam.get("q");

                try {
                    const response=await axios.get(`/api/user/search`,{params: { q: query }})
                    results.value = response.data;

                    if(!results.value.quizzes)
                        quizzes.value=[];
                    else
                        quizzes.value=results.value.quizzes;
                } catch(err) {
                    console.error(err)
                }

                try {
                    const response=await axios.get('/api/users/me')
                    user.value=response.data
                } catch(err) {
                    console.log(err)
                }
            })

            async function enrollNow(quiz_id){
                try {
                    const response=await axios.post('/api/enrolls/crud', {user_id:user.value.user_id, quiz_id:quiz_id})
                    success.value=response.data.message
                    console.log("working")
                } catch(err) {
                    console.log(err)
                    error.value = err.response.data.error;
                }
            }

            return{results,quizzes, enrollNow,error,success}
        }
    }).mount("#app")