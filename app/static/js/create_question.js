const { createApp, ref } = Vue;
        createApp({
            setup(){
                const form = ref({ question:'', correct:'', marks:'', options:['','','','']});

                const error= ref('');
                const success= ref('');
                const quiz_id=ref();

                const goBack = () => {
                    window.history.back();
                };

                const submitForm = async () => {
                    error.value=''; success.value='';

                    console.log(form.value)

                    const nonEmptyOptions = form.value.options.filter(opt => opt.trim() !== '');

                    //Integrity checks
                    if(nonEmptyOptions.length<2){
                        error.value="Minimum options are two"
                    }
                        
                    if(!form.value.options[form.value.correct-1]){
                        error.value="Correct Option and Options do not match"
                    }

                try {
                        const parts=window.location.pathname.split('/');
                        quiz_id.value=parseInt(parts[parts.length-3]);

                        const response= await axios.post(`/api/quizzes/${quiz_id.value}/questions/crud`, {question:form.value.question, correct:form.value.correct, marks:form.value.marks, options:form.value.options, quiz_id:quiz_id.value});
                        success.value=response.data.message;


                        form.value={ question:'', correct:'', marks:'', options:['','','','']};


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