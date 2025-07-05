const { createApp, ref, onMounted }=Vue;
createApp({
    setup(){
        const SubjectObj=ref({ id:'', name:'', desc:'' });
        const Chapters=ref([]);

        const error=ref("");
        const success=ref("");

        const goBack = () => {
                    window.history.back();
                };

        onMounted(async () => {
            const parts=window.location.pathname.split('/');
            SubjectObj.value.id=parseInt(parts[parts.length-1]);

            try {
                const response1 = await axios.get(`/api/subjects/${SubjectObj.value.id}`);
                SubjectObj.value=response1.data;

                const response2 = await axios.get(`/api/subjects/${SubjectObj.value.id}/chapters/crud`);
                Chapters.value=response2.data;
                console.log(Chapters.value);

            } catch(err) {
                console.error("Smth went wrong:"+err)
            }
        });

        const confirmDelete=async (chap_id) => {
                const sure=confirm("Are you sure? This will delete subject and all related quizzes, questions and data");
                if(!sure) return;
                
                try {
                    await axios.delete(`/api/subjects/${SubjectObj.value.id}/chapters/crud/${chap_id}`);
                    success.value="Subject deleted successfully!";

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

        return { SubjectObj, Chapters, goBack, confirmDelete, error, success };


    }
}).mount("#app");