
var app = new Vue({
    el: '#app',

    //DATA
    data: {
        serviceURL: "https://info3103.cs.unb.ca:8001",
        authenticated: false,
        signedIn: null,
        imagesData: null,
        //Boolean values for displaying divs
        viewUpload: false,
        viewImages: false,
        viewImageSelected: false,
        viewUserProfile: false,
	confirmDelete: false,
        //the image file selected from the upload div
        uploadData: {
            imageFile: '',
            description:''
        //login info
        },
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
                            this.signedIn = response.data.userId;
                            this.viewImages = true;
                            this.fetchImages();
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
                    this.authenticated = false;
                    location.reload();
                })
                .catch(e => {
                    console.log(e);
                });
        },
	deleteUser()  {
	    axios
                .delete(this.serviceURL + '/users/'+this.signedIn.toString())
                .then(response =>{
                    this.authenticated = false;
                    location.reload();
                })
                .catch(e => {
                    console.log(e);
                });
        },

        startUpload() {
            this.viewImages=false;
            this.viewImageSelected = false;
            this.viewUserProfile = false;
            this.viewUpload= true;
        },

	viewProfile() {
            this.viewImages=false;
            this.viewImageSelected = false;
            this.viewUserProfile = true;
            this.viewUpload= false;

        },

	viewDeleteUser(){
	    this.confirmDelete=true;
	},

	cancelDelete(){
	    this.confirmDelete=false;
	},

        fetchImages(){
           axios
                .get(this.serviceURL+'/users/'+this.signedIn.toString()+'/images')
                .then(response => {
                    this.imagesData = response.data.images;
                })
                .catch(e =>{
                    alert("Unable to load user images");
                    console.log(e);
                })
        },

        selectImage() {

        },

        handleImage(){
            //Keep the file variable in the data object up to date
            this.uploadData.imageFile = this.$refs.file.files[0];
        },
       
        uploadImage() {
            let formData = new FormData();
            //append the file from the data object
            formData.append('file', this.uploadData.imageFile);

            //Check if the is an inputted description and add it
            console.log(this.uploadData.description);
            if (!this.uploadData.description == "") {
                formData.append('description', this.uploadData.description);
            }

            axios
                .post(this.serviceURL + '/users/'+this.signedIn.toString()+'/images',
                     formData,
                     {
                         headers: {
                             'Content-type': 'multipart/form-data'
                         }
                     })
                .then(response =>{
                    alert("success");
                })
                .catch(e => {
                    console.log(e);
                });


        }

    }
});
