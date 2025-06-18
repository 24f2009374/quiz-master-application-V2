const { createApp, ref } = Vue;

        createApp({
            setup(){
                const form = ref({ email:'', password:'' });

                const error= ref('');

                const loginUser = async () => {
                    error.value='';

                    if(!form.value.email || !form.value.password){
                        error.value="Both fields are Requried";
                        return;
                    }

                    try {
                        const response = await axios.post('/api/login', {email:form.value.email, password:form.value.password});

                        if(response.data.redirect){
                            window.location.href=response.data.redirect;
                            
                        }
                    } catch(err) {
                        error.value = err.response?.data?.error || "Login failed.";
                    }
                };
                return { form, error, loginUser };
            }
        }).mount("#app")