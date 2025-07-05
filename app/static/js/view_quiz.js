const { createApp, ref, onMounted }=Vue;
createApp({
    setup(){
        const quizObj=ref({ id:'', name:'', time:'', date:'' });
        const Questions=ref([]);
        const total=ref(0);
        let ques; let i;

        const error=ref("");
        const success=ref("");

        const confirmDelete=async (q_id) => {
            const sure=confirm("Are you sure? This will delete the question");
            if(!sure) return;
            
            try {
                await axios.delete(`/api/quizzes/${quizObj.value.id}/questions/crud/${q_id}`);
                success.value="Subject deleted successfully!";

                setTimeout(() => {
                    window.location.reload();
                }, 800);
            } catch(err) {
                error.value=err;
            }
        };


        const goBack = () => {
                    window.history.back();
                };

        onMounted(async () => {
            const parts=window.location.pathname.split('/');
            quizObj.value.id=parseInt(parts[parts.length-1]);

            try {
                const response1 = await axios.get(`/api/quizzes/${quizObj.value.id}`);
                quizObj.value=response1.data;

                const response2 = await axios.get(`/api/quizzes/${quizObj.value.id}/questions/crud`);
                Questions.value=response2.data;
                

                for(i=0; i<Questions.value.length; i++){
                    ques=Questions.value[i];
                    const filteredOptions = ques.options.filter(opt => opt !== null);
                    ques.options=filteredOptions;
                }

            } catch(err) {
                console.error("Smth went wrong:"+err)
            }

            for(i=0; i<Questions.value.length; i++){
                ques=Questions.value[i];
                total.value+=parseInt(ques.marks);
                console.log(total.value)
            }

        
            window.addEventListener("pageshow", function (event) {
                if (event.persisted) {
                    window.location.reload();
                }
            });

        });

        return { quizObj, Questions, goBack, total, confirmDelete, success, error };


    }
}).mount("#app");