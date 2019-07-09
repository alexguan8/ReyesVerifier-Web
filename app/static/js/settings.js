$(document).ready(function() {
    var return_value = prompt("Password:");
    if (return_value === "reyesrocks") {
        //do nothing
    } else {
        window.location.href = "/index";
    }
});