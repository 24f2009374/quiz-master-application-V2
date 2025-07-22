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
                    
                    const ctx= document.getElementById("scoreChart").getContext('2d')
                    new Chart(ctx, {
                        type:'line',
                        data:{
                            labels:label_data,
                            datasets:[{
                                label:'Your Scores',
                                data:mark_data,
                                borderColor:'rgba(255, 99, 132, 1)',
                                backgroundColor:'rgba(192, 192, 192, 1)',
                                borderWidth:2

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