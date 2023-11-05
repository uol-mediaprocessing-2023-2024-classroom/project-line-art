<template>
    <v-container>
        <h1>hey</h1>
        <v-btn @click="mainPage">MainPage</v-btn>
    </v-container>
</template>

<script>
    export default {
        name: 'LoginPage',
    

    methods:  {
        mainPage() {
            console.log("hey from login")
            this.$emit("switchSide");
        }
    }
    }
</script>
