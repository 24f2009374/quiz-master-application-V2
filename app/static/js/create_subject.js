const { createApp, ref } = Vue;
        createApp({
            setup(){
                const form = ref({ sub_name:'', sub_text:'' });

                const error= ref('');
                const success= ref('');

                const submitForm = async () => {
                    error.value=''; success.value='';

                    try {
                        const response= await axios.post('/api/subjects/crud', {sub_name:form.value.sub_name, sub_desc:form.value.sub_text});
                        success.value=response.data.message;
                        console.log(success.value);

                        form.value={ sub_name:'', sub_text:'' };


                    } catch(err) {
                        if (err.response && err.response.data && err.response.data.error) {
                            error.value = err.response.data.error;
                        } else {
                            error.value = "Creation failed.";
                    }
                    }

                };

                return {
                    form,
                    error,
                    success,
                    submitForm
                };
            }
        }).mount("#app");