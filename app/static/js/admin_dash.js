const { createApp, ref, onMounted, computed } = Vue;

    createApp({
        setup() {
            const panelOpen=ref(false);
            const subjects=ref([]);

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
                    console.log(subjects.value)
                    console.log(response.data)
                } catch(err) {
                    console.error("Smth went wrong:"+err)
                }
            }

            const contentCalc=computed(()=> ({
                transition: 'margin-top 0.4s ease',
                marginTop: panelOpen.value ? PanelHeight + 'px' : '0px'
            }));

            return { panelOpen, togglePanel, subjects, contentCalc };
        }
    }).mount('#app');