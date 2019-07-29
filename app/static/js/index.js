$(document).ready(function() {
    var username_value = prompt("Username");
    var return_value = prompt("Password:");

    var spawn = require("child_process").spawn,
        child;
    var shellPath = path.join(__dirname, '..', '..', 'AD_Authenticate.ps1', ' ' + username_value, ' ' + return_value)
    child = spawn("powershell.exe", [shellPath]);

    child.stdout.on("data", function(data) {
        console.log("Powershell Data: " + data);
    });
    child.stderr.on("data", function(data) {
        console.log("Powershell Errors: " + data);
    });
    child.on("exit", function() {
        console.log("Powershell Script finished");
    });




    if (return_value === "reyespassword") {
        reset();
        resetInput();
    } else {
        //redirect back to home
        window.location.href = "/index";
    }
});

$("#exampleInputEmail1").change(function(e) {
    e.preventDefault();

    $("input#usernameHidden").val($(this).val())
});

$('#csvFileInput').on('change', function() {
    //get the file name
    var pathwithfilename = $(this).val();
    var fileName = pathwithfilename.substring(12);
    //replace the "Choose a file" label
    $(this).next('.custom-file-label').html(fileName);
})

$('.dropdown-menu a').click(function() {
    $('#selected').text($(this).text());
    $('input#selectedHidden').val($(this).text());

    selec = $(this).text();

    if (selec == "Sales") {
        $('#formatPrompt').text("Filename should be of format xxx_Sales.csv");
    } else if (selec == "Payroll") {
        $('#formatPrompt').text("Filename should be of format xxx_Payroll.csv");
    } else if (selec == "Inventory") {
        $('#formatPrompt').text("Filename should be of format xxx_Inventory.csv");
    } else if (selec == "Static Percentages") {
        $('#formatPrompt').text("Filename should be of format xxx_Static_Percentage.csv");
    }
});

$('#fileForm').submit(function(event) {
    var formId = $(this).attr('id');
    upload(request_url);

    event.preventDefault();

});

// Get a reference to the progress bar, wrapper & status label
var progress = document.getElementById("progress");
var progress_wrapper = document.getElementById("progress_wrapper");
var progress_status = document.getElementById("progress_status");

// Get a reference to the 3 buttons
var upload_btn = document.getElementById("upload_btn");
var loading_btn = document.getElementById("loading_btn");
var cancel_btn = document.getElementById("cancel_btn");

// Get a reference to the alert wrapper
var alert_wrapper = document.getElementById("alert_wrapper");

// Get a reference to the file input element & input label and input type label
var input = document.getElementById("csvFileInput");
var file_input_label = document.getElementById("file_input_label");

// Get a reference to the file type button and hidden tracker
var file_type_drop = document.getElementById("selected");
var file_type_hidden = document.getElementById("selectedHidden")

// Function to show alerts
function show_alert(message, alert) {

    alert_wrapper.innerHTML = `
        <div id="alert" class="alert alert-${alert} alert-dismissible fade show" role="alert">
            <span class = "font-weight-bold">${message}</span>
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `
}

// Function to upload file
function upload(url) {
    // Reject if the file input is empty & throw alert
    if (!input.value) {

        show_alert("No file selected", "warning")

        return;
    }

    if (!file_type_hidden.value) {

        show_alert("No file type selected", "warning")

        return;
    }

    // Create a new FormData instance
    var data = new FormData();

    // Create a XMLHTTPRequest instance
    var request = new XMLHttpRequest();

    // Set the response type
    request.responseType = "json";

    // Clear any existing alerts
    alert_wrapper.innerHTML = "";

    // Disable the input during upload
    input.disabled = true;

    // Hide the upload button
    upload_btn.classList.add("d-none");

    // Show the loading button
    loading_btn.classList.remove("d-none");

    // Show the cancel button
    cancel_btn.classList.remove("d-none");

    // Show the progress bar
    progress_wrapper.classList.remove("d-none");

    // Get a reference to the file
    var file = input.files[0];

    // Get a reference to the filename
    var filename = file.name;

    // Get a reference to the filesize & set a cookie
    var filesize = file.size;
    document.cookie = `filesize=${filesize}`;

    // Append the file to the FormData instance
    data.append("file", file);

    value = $("#selectedHidden").val();
    data.append("fileTypeData", value)
    data.append("usernameData", $("#usernameHidden").val())

    // request progress handler
    request.upload.addEventListener("progress", function(e) {

        // Get the loaded amount and total filesize (bytes)
        var loaded = e.loaded;
        var total = e.total

        // Calculate percent uploaded
        var percent_complete = (loaded / total) * 100;

        // Update the progress text and progress bar
        progress.setAttribute("style", `width: ${Math.floor(percent_complete)}%`);
        progress_status.innerText = `${Math.floor(percent_complete)}% uploaded`;

    })

    // request load handler (transfer complete)
    request.addEventListener("load", function(e) {
        if (request.status == 200) {
            if (`${request.response.valid}` == "true") {
                show_alert(`${request.response.message}`, "success");
            } else {
                show_alert(`${request.response.message}`, "danger");
            }

        } else {

            show_alert(`Error uploading file`, "danger");

        }

        reset();

    });

    // request error handler
    request.addEventListener("error", function(e) {

        reset();

        show_alert(`Error uploading file`, "warning");

    });

    // request abort handler
    request.addEventListener("abort", function(e) {

        reset();
        resetInput();

        show_alert(`Upload cancelled`, "primary");

    });

    // Open and send the request
    request.open("post", url);
    request.send(data);

    cancel_btn.addEventListener("click", function() {

        request.abort();
        reset();
        resetInput();

    })

}

function resetInput() {
    input.value = null;
}

// Function to reset the page
function reset() {

    // Hide the cancel button
    cancel_btn.classList.add("d-none");

    // Reset the input element
    input.disabled = false;

    // Show the upload button
    upload_btn.classList.remove("d-none");

    // Hide the loading button
    loading_btn.classList.add("d-none");

    // Hide the progress bar
    progress_wrapper.classList.add("d-none");

    // Reset the progress bar state
    progress.setAttribute("style", `width: 0%`);

    // Reset the input placeholder
    file_input_label.innerText = "Select file";

    // Reset file input
    document.querySelector('#csvFileInput').value = ''

    // Reset file type dropdown button and hidden tracker
    file_type_drop.innerHTML = "File Type";
    file_type_hidden.value = "";

    $('#formatPrompt').text("");

}