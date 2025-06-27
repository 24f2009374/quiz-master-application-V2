const { createApp, ref, onMounted }=Vue;
createApp({
    setup(){
        const SubjectObj=ref({ id:'', name:'', desc:'' });
        const Chapters=ref([])

        onMounted(async () => {
            const parts=window.location.pathname.split('/');
            SubjectObj.value.id=parseInt(parts[parts.length-1]);

            try {
                const response1 = await axios.get(`/api/subjects/${SubjectObj.value.id}`);
                SubjectObj.value=response1.data;

                const response2 = await axios.get(`/api/subjects/${SubjectObj.value.id}/chapters/crud`);
                Chapters.value=response2.data;
                console.log(Chapters.value);

            } catch(err) {
                console.error("Smth went wrong:"+err)
            }
        });

        return { SubjectObj, Chapters };


    }
}).mount("#app");