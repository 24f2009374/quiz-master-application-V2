const { createApp, ref, onMounted }=Vue;
createApp({
    setup(){
        const ChapObj=ref({ id:'', name:'', desc:'' });
        const Quizzes=ref([]);

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

        return { ChapObj, Quizzes, goBack };


    }
}).mount("#app");