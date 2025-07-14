const { createApp, ref, onMounted, computed }=Vue;
        createApp({
            setup(){
                const questions=ref([]);
                const quizID=parseInt(window.location.pathname.split('/').pop());
                const answers=ref([]);
                const q_time=ref(0);
                const remaining=ref(0);
                const timer=ref(null);
                const attemptStart=ref(null);
                const isLow=ref(false)

                const error=ref("")
                const success=ref("")

                onMounted(async () => {
                    try{
                        const response=await axios.get(`/api/attempt/${quizID}`);
                        questions.value=response.data.questions;
                        q_time.value=response.data.quiz_time;
                        answers.value=new Array(questions.value.length).fill(null);
                        
                        attemptStart.value=new Date().toISOString();

                        remaining.value=q_time.value*60;
                        startTimer()
                    } catch(err){
                        error.value=err
                    }
                });

                function startTimer(){
                    timer.value=setInterval(() => {
                        remaining.value--;
                        if(remaining.value<=300){
                            if(!isLow.value){
                                alert("Low Time!")
                            }
                            isLow.value=true;
                        }

                        if(remaining.value<=0){
                            clearInterval(timer.value)
                            submitQuiz(true)
                        }
                    }, 1000);
                }

                const submitQuiz = async (force=false) => {
                    if(!force){
                        const sure=confirm("Submit Quiz?")
                        if(!sure) return;
                    }

                    const finals={"quiz_id":quizID, "answers":answers.value, "att_start":attemptStart.value, "att_end":new Date().toISOString()};
                    
                    try {
                        console.log("Payload reached Try")
                        await axios.post('/api/attempt/submit', finals);
                        window.location.href="/user/quiz/thank";
                    } catch(err){
                        error.value=err
                        alert(error.value)
                    }
                };

                const pStyle=computed(() => ({
                    color:isLow.value?'red':'white',
                    transition:'color 0.3s ease'
                }))

                return { questions, answers, remaining, submitQuiz, pStyle, error, success }
            }
        }).mount("#app")