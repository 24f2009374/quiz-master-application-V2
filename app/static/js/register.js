const { createApp, ref } = Vue;
        createApp({
            setup(){
                const form = ref({ username:'', email:'', password1:'', password2:'' });

                const error= ref('');
                const success= ref('');

                const submitForm = async () => {
                    error.value=''; success.value='';

                    if (form.value.password1 !== form.value.password2) {
                        error.value="Passwords do not match";
                        return;
                    }

                    if(form.value.password1.length<6){
                        error.value="Password is too Short. 6 Characters."
                        return;
                    }

                    try {
                        const response= await axios.post('/api/register', {username:form.value.username, email:form.value.email, password:form.value.password1});
                        success.value=response.data.message;
                        console.log(success.value);

                        form.value={ username:'', email:'', password1:'', password2:'' };


                    } catch(err) {
                        error.value = err.response?.data?.error || "Registration failed.";
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