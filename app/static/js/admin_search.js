const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const results=ref({});
            const users=ref([])
            const subs=ref([])
            const chaps=ref([])
            const quizzes=ref([])

            onMounted(async () =>{
                const URLParam=new URLSearchParams(window.location.search);
                const query=URLParam.get("q");
                try {
                    const response=await axios.get(`/api/admin/search`,{params: { q: query }})
                    results.value = response.data;
                    if(!results.value.users)
                        users.value=[];
                    else
                        users.value=results.value.users;

                    if(!results.value.subjects)
                        subs.value=[];
                    else
                        subs.value=results.value.subjects;

                    if(!results.value.chapters)
                        chaps.value=[];
                    else
                        chaps.value=results.value.chapters;

                    if(!results.value.quizzes)
                        quizzes.value=[];
                    else
                        quizzes.value=results.value.quizzes;
                    
                    
                        
                } catch(err) {
                    console.error(err)
                }
            })

            const goBack = () => {
                    window.history.back();
                };

            return{results,users,subs,chaps,quizzes, goBack}
        }
    }).mount("#app")