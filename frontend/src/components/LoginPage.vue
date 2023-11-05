<template>
    <v-container>
        <h1>Herzlich willkommen bei LineArt!</h1>
        <v-btn @click="mainPage">MainPage</v-btn>
    </v-container>
</template>

<script>
    export default {
        name: 'LoginPage',
    

    methods:  {
        mainPage() {
            this.$emit("switchSide");
        }
    }
    }
</script>
