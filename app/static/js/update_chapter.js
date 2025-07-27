const { createApp, ref, onMounted } = Vue;
        createApp({
            setup(){
                const form = ref({ chap_name:'', chap_text:'' });

                const error= ref('');
                const success= ref('');

                const chap_id=parseInt(window.location.pathname.split('/').at(-1));
                const chapObj=ref({});

                const goBack = () => {
                    window.history.back();
                };

                onMounted(async () => {
                    try {
                        const response = await axios.get(`/api/chapters/${chap_id}`);
                        chapObj.value=response.data;

                        form.value.chap_name=response.data.name;
                        form.value.chap_text=response.data.desc;

                        console.log(chapObj.value);

                    } catch(err) {
                        error.value=err;
                    }
                    
                })

                const submitForm = async () => {


                    try {
                        await axios.put(`/api/subjects/${chapObj.value.parent}/chapters/crud`, {name:form.value.chap_name, desc:form.value.chap_text, chap_id:chapObj.value.id})
                        success.value = "Chapter updated successfully!";
                        
                        setTimeout(() => {
                            window.location.reload();
                        }, 800);

                    } catch(err) {
                        if (err.response && err.response.data && err.response.data.error) {
                            error.value = err.response.data.error;
                        } else {
                            error.value = "Update failed."+err;
                    }
                    }

                };

                

                return {
                    form, error, success, submitForm, goBack
                };
            }
        }).mount("#app");