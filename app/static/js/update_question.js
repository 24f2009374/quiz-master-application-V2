const { createApp, ref, onMounted } = Vue;
        createApp({
            setup(){
                const form = ref({ question:'', correct:'', marks:'', options:['','','','']});

                const error= ref('');
                const success= ref('');

                const q_id=parseInt(window.location.pathname.split('/').at(-1));
                const quesObj=ref({})

                const goBack = () => {
                    window.history.back();
                };


                onMounted(async () => {
                    try {
                        const response = await axios.get(`/api/questions/${q_id}`);
                        quesObj.value=response.data;

                        form.value.question=response.data.statement;
                        form.value.correct=response.data.correct;
                        form.value.marks=response.data.marks;
                        form.value.options=response.data.options;
                    } catch(err) {}
                    
                })

                const submitForm = async () => {
                    error.value=''; success.value='';

                    console.log(form.value)

                    const nonEmptyOptions = form.value.options.filter(opt => opt !== null);


                    //Integrity checks
                    if(nonEmptyOptions.length<2){
                        error.value="Minimum options are two"
                    }
                        
                    if(!form.value.options[form.value.correct-1]){
                        error.value="Correct Option and Options do not match"
                    }

                    try {
                        await axios.put(`/api/quizzes/${quesObj.value.parent}/questions/crud`, {question:form.value.question, correct:form.value.correct, marks:form.value.marks, options:form.value.options, q_id:quesObj.value.parent})
                        success.value = "Question updated successfully!";
                        
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