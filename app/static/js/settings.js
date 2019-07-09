$(document).ready(function() {
    var return_value = prompt("Password:");
    if (return_value === "reyespassword") {
        //load page
    } else {
        //redirect back to home
        window.location.href = "/index";
    }
});