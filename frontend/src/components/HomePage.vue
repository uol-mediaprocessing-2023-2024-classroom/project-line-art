<template>
    <v-container>
        <div class="header">
            <div class="projektName">
                <h1>
                    LineArt
                </h1>
            </div>
            <div class="userInformation">
                <div>
                    Logged in as: {{ this.userName }}
                </div>
                <div>
                    <input placeholder="Your CEWE cldID" class="idInput" v-model="cldId"/>
                        <!-- Simple button that calls the method 'loadImages' -->
                </div>
            </div>
            <div class="logoutArea">
                <v-btn @click="switchSite">Logout</v-btn>
            </div>
        </div>


        <div class="MainImageArea">
            <!-- selectImageArea -->
            <div class="selectImageArea">
                <div class="subHeader">
                    <h2>Selected Image</h2>
                </div>
                <div class="imageArea">
                    <img class="selectedImg" v-bind:src="selectedImage.url" />
                </div>
            </div>
            <!-- optionArea -->
            <div class="optionArea" >
                <div class="subHeader">

                </div>
                <div style="display: flex; flex-grow: 1; flex-direction: column;">
                    <button class="basicButton" @click="loadImages(cldId)">
                        Load Images
                    </button>
                    Settings:
                    <div class="selectSegmentOption">

                    </div>
                    <button class="basicButton" @click="processImage(selectedImage.id)">
                        Process
                    </button>
            </div>
            </div>
            <!-- processedImageArea -->
            <div class="processedImageArea">
                <div class="subHeader">
                    <h2>Processed Image</h2>
                </div>
                <div class="imageArea">
                    <img class="selectedImg" v-bind:src="processedImage.url" />
                </div>
            </div>

        </div>
  
        <div class="imageGalleryField">
            Images:

            <div>
                <v-row>
                    <v-col v-for="n in galleryImageNum" :key="n" class="d-flex child-flex" cols="2">
                        <v-img :src="currentGallery[n - 1].url" aspect-ratio="1" max-height="200" max-width="200" class="grey lighten-2" @click="updateSelected(currentGallery[n - 1].id)">
                            <template v-slot:placeholder>
                                <v-row class="fill-height ma-0" align="center" justify="center">
                                    <v-progress-circular indeterminate color="grey lighten-5"></v-progress-circular>
                                </v-row>
                            </template>
                        </v-img>
                    </v-col>
                </v-row>
            </div>
            <!--<button class="loadMoreBtn" @click="$emit('loadMore')">Load more</button>-->
        </div>
    </v-container>
</template>

<script>
export default {
    name: "HomePage",

    data() {
        return {
            // User related data
            cldId: "",
            userName: "",
            isLoggedIn: false,

            // Image related data
            imageInfo: {
                name: "",
                avgColor: ""
            },

            // UI related
            loginButtonText: "LOGIN",
        };
    },

    props: {
        selectedImage: Object,
        currentGallery: Array,
        processedImage: Object
    },

    methods: {

        //Switching sites
        switchSite() {
            this.$emit("switchSite");
        },
        // --- IMAGE RELATED METHODS ---

        // Emit a loadImages event.
        loadImages() {
            this.$emit("loadImages", this.cldId);
        },

        // Emit a updateSelected event with the ID of the selected image.
        // This method is called when the user clicks/selects an image in the gallery of loaded images.
        updateSelected(selectedId) {
            this.$emit("updateSelected", selectedId, this.cldId);
        },

        // Emit a processImage event with the ID of the selected image.
        processImage(selectedId) {
            this.$emit("processImage", selectedId, this.cldId);
        },
    },

    computed: {
        /*
            The numer of images within currentGallery can dynamically change after the DOM is loaded. Since the size of the image gallery depends on it,
            it's important for it to be updated within the DOM aswell. By using computed values this is not a problem since Vue updates the DOM in accordance wit them.
        */
        galleryImageNum() {
            return this.currentGallery.length;
        },

        isUserNameEmpty: function () {
            return this.userName == "";
        },
    },

    watch: {

        // Watcher function for updating the displayed image information.
        selectedImage: function () {
            this.imageInfo = {
                name: "Name: " + this.processImage.name,
                avgColor: "Average color: " + this.processImage.avgColor,
            };
        },
    },

    mounted() {
        // Load from local storage
        if (localStorage.isLoggedIn === "true") {
            this.cldId = localStorage.cldId;
            this.userName = localStorage.userName;
            this.isLoggedIn = true;
        }
    },
};
</script>

<style scoped>

/* Header CSS */
.header {
    display: flex;
    flex-direction: row;
    border-radius: 10px;
    padding: 1%;
    overflow-y: auto;
    flex-grow: 1;
    background-color: rgb(249, 251, 255);
}

.projektName {
    display: flex;
    flex-direction: row;
    border-radius: 10px;
    padding: 1%;
    float: left;
    flex-grow: 2;

}

.userInformation {
    display: flex;
    flex-direction: column;
    border-radius: 10px;
    padding: 1%; 
    align-self: center;
    flex-grow: 1;
}
.logoutArea {
    display: flex;
    flex-direction: row;
    border-radius: 10px;
    padding: 1%;
    align-self: end;
    align-items: center;
}

/* Main Area CSS */


.MainImageArea {
    display: flex;
    flex-direction: row ;
    padding: 1%;

}
.selectImageArea {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    align-items: center;
}

.optionArea {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-left: 10px;
    width: 400px;
    flex-grow: 1;
}

.selectSegmentOption{
    display: flex;
    border-radius: 10px;
    padding: 1%;
    overflow-y: auto;
    flex-grow: 1;
    background-color: rgb(249, 251, 255);
}

/* Kann vielleicht mit selectImageArea zusammen gelegt werden */
.processedImageArea {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    align-items: center;
}

.subHeader {
    height: 10%;
    padding-bottom: 2%;
    margin-bottom: 1%;
}
.selectedImageField {
    display: flex;
    flex-direction: row;
    background-color: rgb(249, 251, 255);
    border-radius: 10px;
    box-shadow: 0 10px 10px 10px rgba(0, 0, 0, 0.1);
    color: black;
    padding: 1%;
}

.imageGalleryField {
    display: flex;
    flex-direction: column;
    
    border-radius: 10px;
    color: black;
    padding: 1%;
    margin-top: 1%;
    max-height: 600px;
    overflow-y: auto;
}

.selectedImg {
    max-width: 450px;
    max-height: 450px;
}

.selectedImageInfo {
    margin-left: 10px;
}

.basicButton {
    background-color: rgb(249, 251, 255);
    padding: 0px 4px 0px 4px;
    margin-right: 5px;
    border-radius: 3px;
    width: 150px;
    margin: 3px;
}

.idInput {
    margin-right: 8px;
    border: 1px solid #000;
    border-radius: 3px;
    display: flex;
    flex-grow: 1;
    width: 90%;
}

.loginField {
    display: flex;
    margin-left: auto;
    margin-bottom: 12px;
}

.loginField * {
    margin: 0px 5px 0px 5px;
}

.loginField * input {
    border: 1px solid #000;
    border-radius: 3px;
}

.inputField {
    display: flex;
    flex-direction: column;
    margin-left: 10px;
    width: 400px;
}

.inputField * {
    margin: 5px 0px 5px 0px;
}

.loadMoreBtn {
    background-color: #a7a7a7;
    border-radius: 6px;
    padding-left: 5px;
    padding-right: 5px;
    width: 100px;
    align-self: center;
    margin-top: 10px;
}
</style>
