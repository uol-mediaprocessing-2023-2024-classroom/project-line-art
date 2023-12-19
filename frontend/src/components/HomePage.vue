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
                <v-btn  @click="logout">Logout</v-btn>
            </div>
        </div>
       
        <div class="MainImageArea">
            <!-- selectImageArea -->
            <div class="selectImageArea">
                <div>
                    <h2>Selected Image</h2>
                </div>
                <div v-if="errorMessage" class="error-message">
                    <v-btn variant="text" style="background-color: transparent; box-shadow: none; shape-image-threshold: inherit;">
                        <svg-icon type="mdi" :path="pathInformation"></svg-icon>
                    </v-btn>
                    {{ errorMessage }}
                </div>
                <div class="imageArea">
                    <img class="selectedImg" v-bind:src="selectedImage.url" />
                </div>
            </div>
            <!-- optionArea -->
            <div class="optionArea">
                <div class="subHeader">

                </div>
                <div style="display: flex; flex-grow: 1; flex-direction: column;">
                    Settings:
                    <div class="selectSegmentOption">
                        <v-radio-group>
                            <v-radio label="No colored Segments" value="no Segments" true-value></v-radio>
                            <v-radio label="Image-based color" value="Image-based color" ></v-radio>
                            <v-radio label="Select Color" value="Select Color"></v-radio>
                            <v-color-picker hide-canvas hide-inputs style="min-width: 200px; margin-right: 20PX;"></v-color-picker>
                        </v-radio-group>
                    </div>
                    <button class="basicButton" @click="processImage(selectedImage.id)">
                        Process
                    </button>
            </div>
            </div>
            <!-- processedImageArea -->
            <div class="processedImageArea">
                <div>
                    <h2>Processed Image</h2>
                </div>
                <div v-if="informationImage" class="empty-placeholder">
                    <v-btn variant="text" style="background-color: transparent; box-shadow: none; shape-image-threshold: inherit;">
                        <svg-icon type="mdi" ></svg-icon>
                    </v-btn>
                    {{ informationImage }}
                </div>
                <div class="imageArea">
                    <div v-if="loading" class="loading-overlay">
                        Loading...
                    </div>
                    <img v-else class="selectedImg" v-bind:src="processedImage.url" />
                </div>
            </div>

        </div>
  
        <div class="imageGalleryField">
            <div style="display: flex; flex-direction: row ;">
                Images: 
                <v-btn @click="loadImages(cldId)" variant="text" style="background-color: transparent; box-shadow: none; shape-image-threshold: inherit;">
                    <svg-icon type="mdi" :path="path"></svg-icon>
                </v-btn>
            </div>
           
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
import SvgIcon from '@jamescoyle/vue-icon';
import { mdiReload } from '@mdi/js';
import { mdiInformation } from '@mdi/js';

export default {
    name: "HomePage",
        components: {
            SvgIcon
        },

    data() {
        return {
            // User related data
            cldId: "",
            userName: "",
            isLoggedIn: false,
            path: mdiReload,
            pathInformation: mdiInformation,
            // Image related data
            imageInfo: {
                name: "",
                avgColor: ""
            },

            // UI related
            loginButtonText: "LOGIN",
            errorMessage: null,
            informationImage: null,
            loading: false, // Ladeeffekt aktivieren/deaktivieren
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

        // Helper method called by login(), logs out the user.
        // Also resets saved website data.
        async logout() {
            if (!this.isLoggedIn) return;

            const response = await this.sendLogoutRequest();
            this.handleLogoutResponse(response);

            this.switchSite();
        },

         // Helper method for clearing user data from the browsers local storage.
         handleLogoutResponse() {
            localStorage.cldId = "";
            localStorage.userName = "";
            localStorage.isLoggedIn = false;
            this.resetData();
        },

        // Helper method for resetting saved data.
        resetData() {
            this.cldId = "";
            this.isLoggedIn = false;
            this.userName = "";
            this.loginData = {
                email: "",
                password: ""
            };
            this.imageInfo = {
                name: "",
                avgColor: ""
            };
            this.$emit("resetGallery");
        },
        
        async sendLogoutRequest() {
            const requestOptions = {
                method: "DELETE",
                headers: {
                    cldId: this.cldId,
                    clientVersion: "0.0.1-medienVerDemo",
                },
            };

            try {
                const response = await fetch("https://cmp.photoprintit.com/api/account/session/?invalidateRefreshToken=true", requestOptions);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response;
            } catch (error) {
                this.handleRequestError(error);
                return null;
            }
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
            // Setze die Fehlermeldung auf null, wenn die Verarbeitung erfolgreich ist
            this.errorMessage = null;
            this.informationImage = null;
        },

        // Emit a processImage event with the ID of the selected image.
        processImage(selectedId) {
            // Füge hier den Code für die Fehlerüberprüfung ein
            if(!selectedId || selectedId === "placeholder"){
                // Wenn selectedId nicht vorhanden ist, setze die Fehlermeldung
                this.errorMessage = "Please select a picture!";
                this.informationImage = " ";
                return; // Beende die Methode, um zu verhindern, dass der Rest des Codes ausgeführt wird
            } else{
                // Fortfahren mit der Bildverarbeitung
                this.$emit("processImage", selectedId, this.cldId);
            }
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

            this.$emit("loadImages", this.cldId);
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
    height: 100%;
    flex-grow: 1;
}

.selectSegmentOption{
    display: flex;
    overflow-y: auto;
    flex-grow: 1;
    align-items: center;
    margin-right: 5%;
    height: 70%;
    background-color: rgb(249, 251, 255);
}

.selectSegmentOptionForm{
    display: flex;
    padding: 5%;
    border-color: rgb(249, 251, 255);
}

/* Kann vielleicht mit selectImageArea zusammen gelegt werden */
.processedImageArea {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    align-items: center;
}

.subHeader {
    min-height: 50px;
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
    max-width: 430px;
    max-height: 500px;
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
    align-self: center;
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

.error-message {
  color: red;
}

.empty-placeholder {
  background-color: transparent; /* Hintergrundfarbe der leeren Zeile */
}

.loading-overlay {
background-color: #F3F3F3;
  min-width: 430px;
  min-height: 290px;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  max-width: 430px;
  max-height: 500px;
}
</style>
