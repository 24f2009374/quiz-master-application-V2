const { createApp, ref, onMounted }=Vue;
    createApp({
        setup(){
            const setColors=[
                            'rgba(255, 99, 132, 0.5)',
                            'rgba(255, 159, 64, 0.5)',
                            'rgba(255, 205, 86, 0.5)',
                            'rgba(75, 192, 192, 0.5)',
                            'rgba(54, 162, 235, 0.5)',
                            'rgba(153, 102, 255, 0.5)',
                            'rgba(201, 203, 207, 0.5)'
                            ]
            const setColorsBorders=[
                            'rgb(255, 99, 132)',
                            'rgb(255, 159, 64)',
                            'rgb(255, 205, 86)',
                            'rgb(75, 192, 192)',
                            'rgb(54, 162, 235)',
                            'rgb(153, 102, 255)',
                            'rgb(201, 203, 207)'
                            ]

            onMounted(async () => {
            const top_res=await axios.get('/api/charts', {params:{ctx:"TopUsers"}})
            
            const top_labels = top_res.data.labels
            const top_data = top_res.data.data

            const ctx1 = document.getElementById('topUsersChart')
            const ctx2 = document.getElementById('mostAttempts')
            const ctx3 = document.getElementById('topQuizzes')
            new Chart(ctx1, {
                type:'bar',
                data:{
                    labels:top_labels,
                    datasets:[{
                        label:"Total Marks (Latests)",
                        data:top_data,
                        backgroundColor: ['rgba(75, 192, 192, 0.5)', 'rgba(255, 99, 132, 0.5)', 'rgba(255, 159, 64, 0.5)'],
                        borderColor:['rgb(75, 192, 192)', 'rgb(255, 99, 132)', 'rgb(255, 159, 64)'],
                        borderWidth: 1,
                        borderRadius:2
                    }]
                },
                options:{
                    responsive:true,
                    plugins:{
                        legend:{display:false},
                        title:{display:true, text:"Top 3 Users Across Quizzes"},

                    }
                },
                scales:{
                    y:{beginAtZero:true}
                }
            })
           
            const attempt_res=await axios.get('/api/charts', {params:{ctx:"TopAttempts"}})

            const att_labels=attempt_res.data.labels
            const att_data=attempt_res.data.data

            new Chart(ctx2, {
                type:'bar',
                data:{
                    labels:att_labels,
                    datasets:[{
                        label:"Most Attempts",
                        data:att_data,
                        backgroundColor:setColors ,
                        borderColor: setColorsBorders,
                        borderWidth: 1,
                        borderRadius:2
                    }]
                },
                options:{
                    responsive:true,
                    plugins:{
                        legend:{display:false},
                        title:{display:true, text:"Most Attempts"},

                    }
                },
                scales:{
                    y:{beginAtZero:true}
                }
            })

            const quiz_res=await axios.get('/api/charts', {params:{ctx:"TopQuizzes"}})

            const quiz_labels=quiz_res.data.labels
            const quiz_data=quiz_res.data.data

            new Chart(ctx3, {
                type:'bar',
                data:{
                    labels:quiz_labels,
                    datasets:[{
                        label:"Most Attempts",
                        data:quiz_data,
                        backgroundColor: setColors,
                        borderColor: setColorsBorders,
                        borderWidth: 1,
                        borderRadius:2
                    }]
                },
                options:{
                    responsive:true,
                    plugins:{
                        legend:{display:false},
                        title:{display:true, text:"Most Attempts"},

                    }
                },
                scales:{
                    y:{beginAtZero:true}
                }
            })
        })
        }
    }).mount("#app")