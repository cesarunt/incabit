// Get a reference to the progress bar, wrapper & status label
var progressImage = document.getElementById("progressImage");
var progressImage_wrapper = document.getElementById("progressImage_wrapper");
var progressImage_status = document.getElementById("progressImage_status");

// Get a reference to the 3 buttons
var uploadImage_btn = document.getElementById("uploadImage_btn");
var loadingImage_btn = document.getElementById("loadingImage_btn");
// var cancelupImage_btn = document.getElementById("cancelupImage_btn");
var cancelImage_btn  = document.getElementById("cancelImage_btn");
var processImage_btn = document.getElementById("processImage_btn");
var processImage_wrapper = document.getElementById("processImage_wrapper");

// Get a reference to the alert wrapper
var alertImage_wrapper = document.getElementById("alertImage_wrapper");

// Get a reference to the file input element & input label 
var inputImage = document.getElementById("file_image");
var file_image_label = document.getElementById("file_image_label");
var analyticImage_selected = document.getElementById("analyticImage_selected");
var objectImage_selected = document.getElementById("objectImage_selected");

// Get a reference to the 3 buttons
var closeImage_btn  = document.getElementById("closeImage_btn");
var container_prevImage = document.getElementById("container_prevImage");
var container_postImage = document.getElementById("container_postImage");

// Function to show alerts
function showImageAlert(message, alert) {
  alertImage_wrapper.innerHTML = `
    <div id="alertImage" class="alert alert-${alert} alert-dismissible fade show" role="alert" style="line-height:15px;">
      <small>${message}</small>
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  `  
}

// Function to show content output image
function showImageResult(imageOut, imageW) {
  // var width = "auto";
  // if (imageW > 1000) { width = "800px"; }
  container_postImage.innerHTML = ` 
    <img class="card-img-top" src="${imageOut}" style="border: 1px solid #F55; margin: 0 auto;">
  `
}

// Function to set Analytic
function ai_image_selectAnalytic() {
  if (analyticImage_selected.value=="analytic_none") {
    showImageAlert("Seleccione la analítica", "warning")
    return;
  }
  else {
    // Set value to the analytic control
    if (analyticImage_selected.value=="analytic_detectO"){
      objectImage_selected.value = "all"
    }
    if (analyticImage_selected.value=="analytic_loiterP" || analyticImage_selected.value=="analytic_countP" || analyticImage_selected.value=="analytic_searchO"){
      objectImage_selected.value = "persona"
    }
  }
}

// Function to set Object
function ai_image_selectObject() {
  if (objectImage_selected.value=="none") {
    showImageAlert("Seleccione el objeto", "warning")
    return;
  }
}

// Function to upload file
function ai_clicImageProcess() {
  // Hide the Cancel button
  cancelImage_btn.classList.add("d-none");
  // Hide the Process button
  processImage_btn.classList.add("d-none");
  // Clear any existing alerts
  alertImage_wrapper.innerHTML = "";
  // Show the load icon Process
  processImage_wrapper.classList.remove("d-none");
}

// Function to upload file ANALYTIC
function ai_analytic_uploadImage(url) {

  // Reject if the file input is empty & throw alert
  if (!inputImage.value) {
    showImageAlert("Debe seleccionar una imagen", "warning")
    return;
  }
  if (analyticImage_selected.value=="analytic_none") {
    showImageAlert("Debe seleccionar una analítica", "warning")
    return;
  }
  if (objectImage_selected.value=="none") {
    showImageAlert("Debe seleccionar un objeto", "warning")
    return;
  }

  // Create a new FormData instance
  var data = new FormData();
  // Create a XMLHTTPRequest instance
  var request = new XMLHttpRequest();

  // Set the response type
  request.responseType = "json";
  // Clear any existing alerts
  alertImage_wrapper.innerHTML = "";
  // Disable the input during upload
  inputImage.disabled = true;
  // Hide the upload button
  uploadImage_btn.classList.add("d-none");
  // Show the loading button
  loadingImage_btn.classList.remove("d-none");
  // Show the progress bar
  progressImage_wrapper.classList.remove("d-none");

  // Get a reference to the file
  var file = inputImage.files[0];
  // Get a reference to the filesize & set a cookie
  var filesize = file.size;
  var process = "image";

  document.cookie = `filesize=${filesize}`;
  // Append the file to the FormData instance
  data.append("file", file);
  // Append identifier of process IMAGE on media value
  data.append("process", process);

  if (analyticImage_selected.value!="") {
    data.append("analytic", analyticImage_selected.value);
  }
  if (objectImage_selected.value!="") {
    data.append("object", objectImage_selected.value);
  }

  // request progress handler
  request.upload.addEventListener("progress", function (e) {

    // Get the loaded amount and total filesize (bytes)
    var loaded = e.loaded;
    var total = e.total
    // Calculate percent uploaded
    var percent_complete = (loaded / total) * 100;

    // Update the progress text and progress bar
    progressImage.setAttribute("style", `width: ${Math.floor(percent_complete)}%`);
    progressImage_status.innerText = `${Math.floor(percent_complete)}% uploaded`;

  })

  // request load handler (transfer complete)
  request.addEventListener("load", function (e) {
    if (request.status == 200) {
      showImageAlert(`${request.response.message}`, "success");
      // resetImageUpload();
      // Disable the analytic control
      analyticImage_selected.disabled = true;
      // Disable the object control
      objectImage_selected.disabled = true;
      // Hide the loading button
      loadingImage_btn.classList.add("d-none");
      // Hide the progress bar
      progressImage_wrapper.classList.add("d-none");
      // Show the cancel button
      cancelImage_btn.classList.remove("d-none");
      // Show the process button
      processImage_btn.classList.remove("d-none");
    }
    else {
      showImageAlert(`Error cargando archivo`, "danger");
      resetImageUpload();
    }

    if (request.status == 300) {
      showImageAlert(`${request.response.message}`, "warning");
      resetImageUpload();
    }
    
  });

  // request error handler
  request.addEventListener("error", function (e) {
    resetImageUpload();
    showImageAlert(`Error procesando la imagen`, "warning");
  });

  // Open and send the request
  request.open("POST", url);
  request.send(data);

}

// Function to upload file MASK
function ai_mask_uploadImage(url) {

  // Reject if the file input is empty & throw alert
  if (!inputImage.value) {
    showImageAlert("Debe seleccionar una imagen", "warning")
    return;
  }

  // Create a new FormData instance
  var data = new FormData();
  // Create a XMLHTTPRequest instance
  var request = new XMLHttpRequest();

  // Set the response type
  request.responseType = "json";
  // Clear any existing alerts
  alertImage_wrapper.innerHTML = "";
  // Disable the input during upload
  inputImage.disabled = true;
  // Hide the upload button
  uploadImage_btn.classList.add("d-none");
  // Show the loading button
  loadingImage_btn.classList.remove("d-none");
  // Show the progress bar
  progressImage_wrapper.classList.remove("d-none");

  // Get a reference to the file
  var file = inputImage.files[0];
  // Get a reference to the filesize & set a cookie
  var filesize = file.size;
  var process = "image";

  document.cookie = `filesize=${filesize}`;
  // Append the file to the FormData instance
  data.append("file", file);
  // Append identifier of process IMAGE on media value
  data.append("process", process);

  // request progress handler
  request.upload.addEventListener("progress", function (e) {

    // Get the loaded amount and total filesize (bytes)
    var loaded = e.loaded;
    var total = e.total
    // Calculate percent uploaded
    var percent_complete = (loaded / total) * 100;

    // Update the progress text and progress bar
    progressImage.setAttribute("style", `width: ${Math.floor(percent_complete)}%`);
    progressImage_status.innerText = `${Math.floor(percent_complete)}% uploaded`;

  })

  // request load handler (transfer complete)
  request.addEventListener("load", function (e) {
    if (request.status == 200) {
      showImageAlert(`${request.response.message}`, "success");
      // resetImageUpload();
      // Hide the loading button
      loadingImage_btn.classList.add("d-none");
      // Hide the progress bar
      progressImage_wrapper.classList.add("d-none");
      // Show the cancel button
      cancelImage_btn.classList.remove("d-none");
      // Show the process button
      processImage_btn.classList.remove("d-none");
    }
    else {
      showImageAlert(`Error cargando archivo`, "danger");
      resetImageUpload();
    }

    if (request.status == 300) {
      showImageAlert(`${request.response.message}`, "warning");
      resetImageUpload();
    }
    
  });

  // request error handler
  request.addEventListener("error", function (e) {
    resetImageUpload();
    showImageAlert(`Error procesando la imagen`, "warning");
  });

  // Open and send the request
  request.open("POST", url);
  request.send(data);

}

cancelImage_btn.addEventListener("click", function () {
  resetImageStart();
})

// Function to update the input placeholder
function input_image_file() {
  file_image_label.innerText = inputImage.files[0].name;
}

// Function to reset the upload
function resetImageUpload() {
  // Reset the input video element
  inputImage.disabled = false;
  // Show the upload button
  uploadImage_btn.classList.remove("d-none");
  // Hide the loading button
  loadingImage_btn.classList.add("d-none");
  // Hide the progress bar
  progressImage_wrapper.classList.add("d-none");
  // Reset the progress bar state
  progressImage.setAttribute("style", `width: 0%`);
}

// Function to reset the page
function resetImageStart() {
  // Clear the input
  inputImage.value = null;
  inputImage.disabled = false;
  // Reset the input placeholder
  file_image_label.innerText = "Seleccionar archivo";
  // Hide the cancel button
  cancelImage_btn.classList.add("d-none");
  // Hide the process button
  processImage_btn.classList.add("d-none");
  // Hide the alertVideo_wrapper alert
  alertImage_wrapper.innerHTML = ``
  // Show the upload button
  uploadImage_btn.classList.remove("d-none");
}