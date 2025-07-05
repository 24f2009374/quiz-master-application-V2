const { createApp, ref, onMounted, computed } = Vue;

    createApp({
        setup() {
            const panelOpen=ref(false);
            const subjects=ref([]);

            const error=ref("");
            const success=ref("");

            const PanelHeight=150; 

            function togglePanel(){
                panelOpen.value = !panelOpen.value;
                if(panelOpen.value && !subjects.value.length){
                    loadSubjects();
                }
            }

            async function loadSubjects(){
                try {
                    const response = await axios.get('/api/subjects/crud');
                    subjects.value=response.data;
                } catch(err) {
                    console.error("Smth went wrong:"+err)
                }
            }

            const contentCalc=computed(()=> ({
                transition: 'margin-top 0.4s ease',
                marginTop: panelOpen.value ? PanelHeight + 'px' : '0px'
            }));

            const confirmDelete=async (sub_id) => {
                const sure=confirm("Are you sure? This will delete subject and all related chapters, quizzes, questions and data");
                if(!sure) return;
                
                try {
                    await axios.delete(`/api/subjects/crud/${sub_id}`);
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

            return { panelOpen, togglePanel, subjects, contentCalc, confirmDelete, error, success };
        }
    }).mount('#app');