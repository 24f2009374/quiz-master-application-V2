const { createApp, ref } = Vue;
        createApp({
            setup(){
                const form = ref({ chap_name:'', chap_text:'' });

                const error= ref('');
                const success= ref('');
                const sub_id=ref();
                const goBack = () => {
                    window.history.back();
                };

                const submitForm = async () => {

                    try {
                        const parts=window.location.pathname.split('/');
                        sub_id.value=parseInt(parts[parts.length-3]);
                        console.log(sub_id.value)

                        const response= await axios.post(`/api/subjects/${sub_id.value}/chapters/crud`, {chap_name:form.value.chap_name, chap_desc:form.value.chap_text, sub_id:sub_id.value});
                        success.value=response.data.message;


                        form.value={ sub_name:'', sub_text:'' };


                    } catch(err) {
                        if (err.response && err.response.data && err.response.data.error) {
                            error.value = err.response.data.error;
                        } else {
                            error.value = "Creation failed."+err;
                    }
                    }

                };

                return {
                    form,
                    error,
                    success,
                    submitForm, goBack
                };
            }
        }).mount("#app");