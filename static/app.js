
var app = new Vue({
    el: '#app',

    //DATA
    data: {
        serviceURL: "https://info3103.cs.unb.ca:8001",
        authenticated: false,
        signedIn: null,
        isProfileImage: false,
        profileType: null,
        imagesData: null,
        imagesDataLength: null,
        lengthThird: null,
        lengthTwoThird:null,
        imagesIndex: 0,
        //Boolean values for displaying divs
        viewUpload: false,
        viewImages: false,
        viewImageSelected: false,
        viewUserProfile: false,
        //the image file selected from the upload div
        uploadData: {
            imageFile: '',
            description:''
        //login info
        },
        input: {
            username: "",
            password: ""
        },
        selectedImage: {
            imageId: null,
            isDescription: false,
            description: "",
            fileType: "",
            descriptionDefault: "This pic is so cool it doesn't need a tag line"
        },
    },

    //METHODS
    methods: {
        login() {
            if (this.input.username != "" && this.input.password != "") {
                axios
                    .post(this.serviceURL+"/signin", {
                        "username": this.input.username,
                        "password": this.input.password
                    })
                    .then(response => {
                        if (response.data.status == "success") {
                            this.authenticated = true;
                            this.signedIn = response.data.userId;
                            this.isProfileImage = response.data.profileImage;
                            if(this.isProfileImage){
                                this.profileType = response.data.profileType;
                            }
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

        startUpload() {

            this.viewImages=false;
            this.viewImageSelected = false;
            this.viewUserProfile = false;
            this.viewUpload= true;
            $('.custom-file-label').html("Choose image");
        },

        fetchImages(){
           axios
                .get(this.serviceURL+'/users/'+this.signedIn.toString()+'/images')
                .then(response => {
                    this.imagesData = response.data.images;
                    this.imagesDataLength = this.imagesData.length;
                    this.lengthThird = Math.round(this.imagesDataLength/3);
                    this.lengthTwoThird = Math.round(this.imagesDataLength*2 /3);
                    //change views
                    this.viewImages = true;
                    this.viewImageSelected = false;
                    this.viewUpload = false;
                    this.viewUserProfile = false;

                    //clear imageSelected data
                    this.selectedImage.description = "";
                    this.selectedImage.isDescription = false;
                    this.selectedImage.imageId = null;
                })
                .catch(e =>{
                    alert("Unable to load user images");
                    console.log(e);
                });
        },

        selectImage(image) {
           axios
                .get(this.serviceURL + '/users/' + this.signedIn.toString() + '/images/' + image.imageId.toString())
                .then(response => {
                    let resImage = response.data.image;
                    this.selectedImage.imageId = resImage.imageId;
                    if(resImage.description != null) {
                        this.selectedImage.description = resImage.description;
                        this.selectedImage.isDescription = true;
                    }
                    this.selectedImage.fileType = resImage.filetype;

                    //Changing app view
                    this.viewImages = false;
                    this.viewImageSelected = true;
                })
                .catch(e => {
                    alert("Error viewing image");
                    console.log(e);
                });
            //let imageOwner = image.imageId;
            //alert(imageOwner);

        },

        deleteImage(){
            axios
                .delete(this.serviceURL + "/users/" + this.signedIn.toString() + '/images/' + this.selectedImage.imageId.toString())
                .then(response => {
                    alert("Delete successful");
                    this.fetchImages();
                })
                .catch(e => {
                    alert("Delete unsuccessful");
                    console.log(e);
                });
        },

        downloadImage(){
            axios
                .get(this.serviceURL + "/users/" +   this.signedIn.toString() + '/images/' + this.selectedImage.imageId.toString() + '/download' , {responseType: 'blob'})
                .then(response => {
                    let fileURL = window.URL.createObjectURL(new Blob([response.data]));
                    let fileLink = document.createElement('a');

                    fileLink.href = fileURL;
                    let filename = 'download.' + this.selectedImage.fileType;

                    fileLink.setAttribute('download', filename);
                    document.body.appendChild(fileLink);

                    fileLink.click();

                })
                .catch(e => {
                    alert("Error downloading");
                    console.log(e);
                });
        },

        handleImage(){
            //Keep the file variable in the data object up to date
            this.uploadData.imageFile = this.$refs.file.files[0];
            let filename = this.uploadData.imageFile.name;
            $('.custom-file-label').html(filename);
        },
       
        uploadImage() {
            let formData = new FormData();
            if(this.uploadData.imageFile != '' && ["png", "gif", "jpg", "jpeg"].includes(this.uploadData.imageFile.name.split('.')[1])) {

                formData.append('file', this.uploadData.imageFile);

                //Check if the is an inputted description and add it
                if (!this.uploadData.description == "") {
                    formData.append('description', this.uploadData.description);
                }

                axios
                    .post(this.serviceURL + '/users/'+this.signedIn.toString()+'/images', formData, {
                        headers: {
                            'Content-type': 'multipart/form-data'
                        }
                    })
                    .then(response =>{
                        alert("success");
                        this.uploadData.imageFile = "";
                        this.uploadData.description = "";
                        $('.custom-file-label').html("Choose image");
                    })
                    .catch(e => {
                        alert("Error uploading");
                        console.log(e);
                    });
            }
            else{
                alert("Must be a png, gif, jpg, jpeg");
                this.uploadImage.imageFile = '';
                this.uploadData.description = '';
            }
        },

        viewProfile() {
            this.viewImages=false;
            this.viewImageSelected = false;
            this.viewUserProfile = true;
            this.viewUpload= false;
            $('.custom-file-label').html("Choose image");
        },

        uploadProfileImage() {
            let formData = new FormData();
            if(this.uploadData.imageFile != '' && ["png", "gif", "jpg", "jpeg"].includes(this.uploadData.imageFile.name.split('.')[1])) {

                formData.append('file', this.uploadData.imageFile);
                axios
                    .post(this.serviceURL + '/users/'+this.signedIn.toString()+'/uploadprofile', formData, {
                        headers: {
                            'Content-type': 'multipart/form-data'
                        }
                    })
                    .then(response =>{
                        alert("success");
                        this.profileType = this.uploadData.imageFile.name.split('.')[1];
                        console.log(this.profileType);
                        this.isProfileImage = true;
                        this.uploadData.imageFile = "";
                        $('.custom-file-label').html("Choose image");
                    })
                    .catch(e => {
                        alert("Error uploading");
                        console.log(e);
                    });
            }
            else{
                alert("Must be a png, gif, jpg, jpeg");
                this.uploadImage.imageFile = '';
            }
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

        confirmDelete() {
            let confirmVal = confirm("Do you want to continue? This will delete your profile and images. If you sign in again a new profile will be created.");
            if (confirmVal) {
                this.deleteUser();
            }
        },

    }
});
