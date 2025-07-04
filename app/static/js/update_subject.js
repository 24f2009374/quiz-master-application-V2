const { createApp, ref, onMounted } = Vue;
        createApp({
            setup(){
                const form = ref({ sub_name:'', sub_text:'' });

                const error= ref('');
                const success= ref('');

                const sub_id=parseInt(window.location.pathname.split('/').at(-1));
                const subObj=ref({});

                const goBack = () => {
                    window.history.back();
                };

                onMounted(async () => {
                    try {
                        const response = await axios.get(`/api/subjects/${sub_id}`);
                        subObj.value=response.data;

                        form.value.sub_name=response.data.name;
                        form.value.sub_text=response.data.desc;

                    } catch(err) {
                        error.value=err;
                    }
                    
                })

                const submitForm = async () => {
                    error.value=''; success.value='';

                    try {
                        await axios.put(`/api/subjects/crud`, {name:form.value.sub_name, desc:form.value.sub_text, sub_id:subObj.value.id})
                        success.value = "Subject updated successfully!";
                        
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