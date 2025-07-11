const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const Quizzes=ref([]);
            const Enrollments=ref([]);
            const userId = document.getElementById('app').dataset.userId;

             const error=ref("");
            const success=ref("");

            onMounted(async () => {
                try {
                    const response=await axios.get('/api/quizzes');
                    Quizzes.value=response.data;
                    console.log(Quizzes.value)
                } catch(err) {
                    console.error(err)
                }
            });

            async function enrollNow(quiz_id){
                try {
                    const response=await axios.post('/api/enrolls/crud', {user_id:userId, quiz_id:quiz_id})
                    success.value=response.data.message
                    console.log("working")
                } catch(err) {
                    console.log(err)
                    error.value = err.response.data.error;
                }
            }

            return { Quizzes, userId, enrollNow, error, success}

        }
    }).mount("#app")