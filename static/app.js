var app = new Vue({
    el: '#app',

    //DATA
    data: {
        serviceURL: "https://dev.localhost:8001",
        authenticated: false,
        signedIn: null,
        input: {
            username: "",
            password: ""
        }
    },
    selectedImage: {
        imageId: "",
        isDescription: false,
        description: "",
        fileType: ""
    },

    //METHODS
    methods: {
        login() {
            if (this.input.username != "" && this.input.password != "") {
                console.log("username " + this.input.username);
                axios
                    .post(this.serviceURL+"/signin", {
                        "username": this.input.username,
                        "password": this.input.password
                    })
                    .then(response => {
                        if (response.data.status == "success") {
                            this.authenticated = true;
                            this.loggedIn = response.data.userId;
                        }
                    })
                    .catch(e => {
                        alert("The username or password was incorrect, try again");
                        this.input.password="";
                        console.log(e);
                    });
            }
            else {
                alert("Must enter both a unsername and a password");
            }
        },

        logout()  {
            axios
                .delete(this.serviceURL+"/signin")
                .then(response => {
                    location.reload();
                })
                .catch(e => {
                    console.log(e);
                });
        }

    }
});
