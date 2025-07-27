const { createApp, ref, onMounted }=Vue;
createApp({
    setup(){
        const ChapObj=ref({ id:'', name:'', desc:'' });
        const Quizzes=ref([]);

        const error=ref("");
        const success=ref("");

        const goBack = () => {
                    window.history.back();
                };

        onMounted(async () => {
            const parts=window.location.pathname.split('/');
            ChapObj.value.id=parseInt(parts[parts.length-1]);

            try {
                const response1 = await axios.get(`/api/chapters/${ChapObj.value.id}`);
                ChapObj.value=response1.data;

                const response2 = await axios.get(`/api/chapters/${ChapObj.value.id}/quizzes/crud`);
                Quizzes.value=response2.data;

            } catch(err) {
                console.error("Smth went wrong:"+err)
            }
        });

        const confirmDelete=async (quiz_id) => {
                const sure=confirm("Are you sure? This will delete Quiz and all related questions and data");
                if(!sure) return;
                
                try {
                    await axios.delete(`/api/chapters/${ChapObj.value.id}/quizzes/crud/${quiz_id}`);
                    success.value="Quiz deleted successfully!";

                    setTimeout(() => {
                        window.location.reload();
                    }, 800);
                } catch(err) {
                    error.value=err;
                }
            };

            window.addEventListener("pageshow", function (event) {
                if (event.persisted) {
                    window.location.reload();
                }
            });

        return { ChapObj, Quizzes, goBack, confirmDelete, error, success };


    }
}).mount("#app");