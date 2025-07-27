const { createApp, ref, onMounted } = Vue;
        createApp({
            setup(){
                const form = ref({ quiz_name:'', date:'', time:'' });

                const error= ref('');
                const success= ref('');

                const quiz_id=parseInt(window.location.pathname.split('/').at(-1));
                const quizObj=ref({});

                const goBack = () => {
                    window.history.back();
                };

                onMounted(async () => {
                    try {
                        const response = await axios.get(`/api/quizzes/${quiz_id}`);
                        quizObj.value=response.data;

                        form.value.quiz_name=response.data.name;
                        form.value.date=response.data.date;
                        form.value.time=response.data.time;
                        console.log(quizObj.value);

                    } catch(err) {
                        error.value=err;
                    }
                    
                })

                const submitForm = async () => {


                    try {
                        await axios.put(`/api/chapters/${quizObj.value.parent}/quizzes/crud`, {name:form.value.quiz_name, time:form.value.time, date:form.value.date, quiz_id:quizObj.value.id})
                        success.value = "Quiz updated successfully!";
                        
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