<template>
    <v-app>
        <v-main style="background-color: rgb(204,238,255);">
            <!-- Communication between child and parent components can be done using props and events. Props are attributes passed from a parent to a child and can be used within it.
            A child component can emit events, which the parent then may react to. Here "selectedImage" is a prop passed to HomePage. HomePage emits the "fetchImgs" event,
            which triggers the fetchImgs method in App.vue. In this demo this is technically not needed, but since it's a core element of Vue I decided to include it.-->
            <HomePage v-if="home" :selectedImage="selectedImage" :processedImage="processedImage" :currentGallery="currentGallery" @loadImages="loadImages" @updateSelected="updateSelected" @processImage="processImage" @resetGallery="resetGallery" @switchSite="switchSite" @showError="showError" ref="homePage"/>
            <LoginPage v-else @switchSide="switchSite"/>
        </v-main>
    </v-app>
</template> 

<script>
import HomePage from "./components/HomePage";
import placeholder from "./assets/placeholder.jpg";
import LoginPage from "./components/LoginPage.vue";

export default {
    name: "App",

    components: {
        HomePage,
        LoginPage,
    },

    data() {
        return {
            selectedImage: {
                url: placeholder,
                id: "placeholder"
            },
            home: false,
            processedImage:{
                url: placeholder,
                id: "placeholder"
            },
            currentGallery: [],
            allImgData: [],
            limit: 60,
            loadedAmount: 0
        };
    },

    methods: {

        //Switch Websites
        switchSite() {
            this.home = !this.home;
        },
        /* 
          This method fetches the first 60 images from a user's gallery. 
          It first retrieves all image IDs, then it fetches specific image data. 
        */
        async loadImages(cldId) {

            const headers = {
                cldId: cldId,
                clientVersion: "0.0.1-medienVerDemo",
            };

            // Fetch all image IDs from the user's gallery
            const response = await fetch("https://cmp.photoprintit.com/api/photos/all?orderDirection=asc&showHidden=false&showShared=false&includeMetadata=false", {
                headers: headers
            });
            this.allImgData = await response.json();

            // Reset current gallery and loaded amount before fetching new images
            this.currentGallery = [];
            this.loadedAmount = 0;

            // Fetch detailed image info for each image up to the limit
            for (const photo of this.allImgData.photos) {
                if (this.loadedAmount >= this.limit) break;
                this.loadedAmount++;

                // Construct URL for specific image info and fetch data
                const url = `https://cmp.photoprintit.com/api/photos/${photo.id}.jpg?size=300&errorImage=false&cldId=${cldId}&clientVersion=0.0.1-medienVerDemo`;
                const imgResponse = await fetch(url);
                const imgUrl = imgResponse.url;

                // Push image data to current gallery
                this.currentGallery.push({
                    id: photo.id,
                    name: photo.name,
                    avgColor: photo.avgHexColor,
                    timestamp: photo.timestamp,
                    type: photo.mimeType,
                    url: imgUrl
                });
            }
        },

        /* 
          This method updates the currently selected image. 
          It fetches the high-resolution URL of the selected image and updates the selectedImage property. 
        */
        async updateSelected(selectedId, cldId) {
             // Construct URL for fetching the high-resolution image
            const url = `https://cmp.photoprintit.com/api/photos/${selectedId}.org?size=original&errorImage=false&cldId=${cldId}&clientVersion=0.0.1-medienVerDemo`;
            const response = await fetch(url);

            // Find the image data in the current gallery
            const image = this.currentGallery.find((obj) => obj.id === selectedId);

            // Update the selected image with high-resolution URL and other details
            this.selectedImage = {
                url: response.url,
                id: selectedId,
                name: image.name,
                avgColor: image.avgColor,
            };
        },

        /* This method retrieves a processed version of the selected image from the backend. */
        async processImage(selectedId, cldId) {
            this.$refs.homePage.loading = true; // Aktiviere den Ladeeffekt

            const localUrl = `http://127.0.0.1:8000/process-image/${cldId}/${selectedId}`;

            try{
                // Fetch the processed image
                const response = await fetch(localUrl);
                const imageBlob = await response.blob();
                const processedImageUrl = URL.createObjectURL(imageBlob);
                // Update the selected image with the URL of the processed image
                this.processedImage.url = processedImageUrl;
            } catch (error) {
                // Handle error, z.B. zeige Fehlermeldung an
                this.showError("Fehler beim Laden des Bildes.");
                this.$refs.homePage.informationImage = " ";
            } finally {
                this.$refs.homePage.loading = false; // Deaktiviere den Ladeeffekt, unabhängig vom Erfolg/Fehler
            }
        },

        /* This method resets the current gallery and selected image. */
        resetGallery() {

            this.selectedImage = {
                url: placeholder,
                id: "placeholder"
            };
            this.processedImage = {
                url: placeholder,
                id: "placeholder"
            };
            this.currentGallery = [];
        },

        // Methode zum Anzeigen der Fehlermeldung in der HomePage.vue
        showError(errorMessage) {
            // Du könntest hier weitere Aktionen durchführen, z.B. Loggen
            console.error(errorMessage);
            // Aktualisiere die Fehlermeldung in der HomePage.vue
            this.$refs.homePage.errorMessage = errorMessage;
        },
    },
};
</script>
