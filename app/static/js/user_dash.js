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

            const triggerExport=async () => {
                try {
                    const response=await axios.get('/api/charts', {params:{ctx:"CSV"}})
                    alert("Export initiated - You will receive a download link shortly");
                } catch(err) {
                    console.log(err)
                    alert("Failed to trigger export");
                }
            }
            return { Enrollments, error, success, triggerExport }
        }
    }).mount("#app")