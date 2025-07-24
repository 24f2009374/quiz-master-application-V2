const { createApp, ref, onMounted } = Vue;
    createApp({
        setup(){
            const Enrollments=ref([]);
            const Quizzes=ref([]);

            const error=ref("");
            const success=ref("");

            const userId = document.getElementById('app').dataset.userId;
            
            onMounted(async () => {
                try {
                    const response=await axios.get(`/api/enrolls/crud/${userId}`);
                    Enrollments.value=response.data
                } catch(err) {
                    console.log(err)
                }
            })

            //Charts
            

            
            return { Enrollments, error, success }
        }
    }).mount("#app")