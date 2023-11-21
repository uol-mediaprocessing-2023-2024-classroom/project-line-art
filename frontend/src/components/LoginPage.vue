<template>
    <v-container>
        <h1>Herzlich willkommen bei LineArt!</h1>
        <div class="loginField">
            <h2>E-mail</h2>
            <input required placeholder="Email" v-model="loginData.email" type="email" name="email" autocomplete="email" />
            <h2>Passwort:</h2>
            <input required placeholder="Password" v-model="loginData.password" type="password" name="password" autocomplete="password" /> 
            <v-btn @click="login" :disabled="awaitingLoginResponse" >
                <v-progress-circular indeterminate color="grey lighten-5" v-if="awaitingLoginResponse"></v-progress-circular>
                <div v-else>
                    {{ this.loginButtonText }}
                </div>
            </v-btn>
        </div>
        <v-btn @click="mainPage">MainPage</v-btn>
    </v-container>
</template>

<script>
    export default {
        name: 'LoginPage',
    
        data() {
            return {

                isLoggedIn: false,
                loginData: {
                    email: "",
                    password: ""
                },
                awaitingLoginResponse: false,

                 // UI related
                loginButtonText: "LOGIN",
            }

        },

    methods:  {
        //Switching sides
        mainPage() {
            this.$emit("switchSide");
        },

        //Authentification Methods

        // Send a login request to the CEWE API test server.
        // If the user is already logged in, send a logout request instead.
        async login() {
            if (this.isLoggedIn) {
                this.logout();
                this.mainPage();
                return;
            }

            if (this.awaitingLoginResponse) return;
            this.awaitingLoginResponse = true;

            const requestOptions = this.getLoginRequestOptions();
            const response = await this.sendLoginRequest(requestOptions);

            if (response) {
                this.handleLoginResponse(response);
            }

            this.awaitingLoginResponse = false;
            this.mainPage();
        },

        // Helper method called by login(), logs out the user.
        // Also resets saved website data.
        async logout() {
            if (!this.isLoggedIn) return;

            const response = await this.sendLogoutRequest();
            this.handleLogoutResponse(response);
        },

        // Helper method for saving user data in the browsers local storage.
        handleLoginResponse(response) {
            this.cldId = response.session.cldId;
            this.userName = response.user.firstname;
            this.isLoggedIn = true;

            localStorage.cldId = this.cldId;
            localStorage.userName = this.userName;
            localStorage.isLoggedIn = this.isLoggedIn;
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
            this.awaitingLoginResponse = false;
            this.$emit("resetGallery");
        },

        // --- REQUEST HANDLERS ---

        getLoginRequestOptions() {
            return {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    clientVersion: "0.0.1-medienVerDemo",
                    apiAccessKey: "6003d11a080ae5edf4b4f45481b89ce7",
                },
                body: JSON.stringify({
                    login: this.loginData.email,
                    password: this.loginData.password,
                    deviceName: "Medienverarbeitung CEWE API Demo",
                }),
            };
        },

        async sendLoginRequest(requestOptions) {
            let status = 0;
            try {
                const response = await fetch("https://cmp.photoprintit.com/api/account/session/", requestOptions);
                status = response.status;
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            } catch (error) {
                this.handleRequestError(error, status);
                return null;
            }
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

        handleRequestError(error, status = 0) {
            console.error("Request failed:", error);
            if (status === 500 || status === 405) {
                this.displayError("Internal error occurred, please try again later.");
            } else if (status >= 400 && status < 500) {
                this.displayError("Entered credentials are incorrect or the request was not properly formatted.");
            } else {
                this.displayError("Something went wrong, please try again.");
            }
        },

        displayError(message) {
            alert(message);
        },
        
    },

    watch: {
        // Watcher function for updating login button text.
        isLoggedIn(isLoggedIn) {
            if (isLoggedIn) {
                this.loginButtonText = "LOGOUT";
            } else {
                this.loginButtonText = "LOGIN";
            }
        },
    },

    mounted() {
        // Load from local storage
        if (localStorage.isLoggedIn === "true") {
            this.cldId = localStorage.cldId;
            this.userName = localStorage.userName;
            this.isLoggedIn = true;
        }
    }

    }
</script>
