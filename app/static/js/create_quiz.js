const { createApp, ref } = Vue;
        createApp({
            setup(){
                const form = ref({ quiz_name:'', date:'', time:'' });

                const error= ref('');
                const success= ref('');
                const chap_id=ref();

                const goBack = () => {
                    window.history.back();
                };

                const submitForm = async () => {
                    error.value=''; success.value='';

                    try {
                        const parts=window.location.pathname.split('/');
                        chap_id.value=parseInt(parts[parts.length-3]);

                        const response= await axios.post(`/api/chapters/${chap_id.value}/quizzes/crud`, {quiz_name:form.value.quiz_name, date:form.value.date, chap_id:chap_id.value, time:form.value.time});
                        success.value=response.data.message;


                        form.value={ quiz_name:'', date:'', time:'' };


                    } catch(err) {
                        if (err.response && err.response.data && err.response.data.error) {
                            error.value = err.response.data.error;
                        } else {
                            error.value = "Creation failed."+err;
                    }
                    }

                };

                return {
                    form, error, success, submitForm, goBack
                };
            }
        }).mount("#app");