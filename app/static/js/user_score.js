const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const error=ref("")
            const success=ref("")
            const quizID=parseInt(window.location.pathname.split('/').pop());
            const scores=ref([])
            let mark_data
            let label_data
            onMounted(async () => {
                try{
                    const response=await axios.get(`/api/scores/${quizID}`);
                    
                    scores.value=response.data

                    //Chart Mounting
                    
                    mark_data=new Array(response.data.length).fill(null);
                    label_data=new Array(response.data.length).fill(null)
                    for(let i=0;i<response.data.length;i++){
                        mark_data[i]=response.data[i].scored
                        label_data[i]=`Attempt ${i+1}`
                    }
                    
                    const ctx1= document.getElementById("scoreChart").getContext('2d')
                    const ctx2= document.getElementById("avgChart").getContext('2d')
                    new Chart(ctx1, {
                        type:'line',
                        data:{
                            labels:label_data,
                            datasets:[{
                                label:'Your Scores',
                                data:mark_data,
                                borderColor:'rgba(255, 99, 132, 1)',
                                backgroundColor:'rgba(192, 192, 192, 1)',
                                borderWidth:2,
                                tension:0.1

                            }]
                        },
                        options:{
                            responsive:true,
                            scales:{
                                y:{beginAtZero:true}
                            }
                        }
                    })

                    // Vs avg
                    const avg_res=await axios.get('/api/charts', {params:{ctx:"userVAvg", "quiz_id":quizID}})
                    

                    const user_scores=avg_res.data.user_scores
                    const avg_scores=avg_res.data.avg_scores

                    console.log(user_scores)

                    const labels=new Array(user_scores.length).fill(null)

                    for(let i=0;i<avg_scores.length;i++)
                        labels[i]=`Attempt ${i+1}`

                    new Chart(ctx2, {
                        type:'line',
                        data:{
                            labels:labels,
                            datasets:[{
                                label:"Your Scores",
                                data:user_scores,
                                backgroundColor:'#36A2EB44',
                                borderColor:'#36A2EB',
                                tension:0.25
                            },
                            {
                                label:"Avg Scores",
                                data:avg_scores,
                                backgroundColor:'#FF638444',
                                borderColor:'#FF6384',
                                tension:0.25
                            }]
                        },
                        options:{
                            responsive:true,
                            scales:{
                                y:{beginAtZero:true}
                            }
                        }
                    })
                } catch(err) {
                    error.value=err
                }
            })

            return { error, success, scores }
        }
    }).mount("#app")