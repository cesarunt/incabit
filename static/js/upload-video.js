// Get a reference to the progress bar, wrapper & status label
var progressVideo = document.getElementById("progressVideo");
var progressVideo_wrapper = document.getElementById("progressVideo_wrapper");
var progressVideo_status = document.getElementById("progressVideo_status");

// Get a reference to the 3 buttons
var uploadVideo_btn = document.getElementById("uploadVideo_btn");
var loadingVideo_btn = document.getElementById("loadingVideo_btn");
var cancelupVideo_btn = document.getElementById("cancelupVideo_btn");
var cancelVideo_btn  = document.getElementById("cancelVideo_btn");
var processVideo_btn = document.getElementById("processVideo_btn");
var processVideo_wrapper = document.getElementById("processVideo_wrapper");

// Get a reference to the alert wrapper
var alertVideo_wrapper = document.getElementById("alertVideo_wrapper");
var alertStream_wrapper = document.getElementById("alertStream_wrapper");

// Get a reference to the file video element & input video label 
var inputVideo = document.getElementById("file_video");
var file_video_label = document.getElementById("file_video_label");
var analyticVideo_selected = document.getElementById("analyticVideo_selected");
var objectVideo_selected = document.getElementById("objectVideo_selected");
var analyticStream_selected = document.getElementById("analyticStream_selected");
var objectStream_selected = document.getElementById("objectStream_selected");

// Function to show alerts
function showVideoAlert(message, alert) {
  alertVideo_wrapper.innerHTML = `
    <div id="alertVideo" class="alert alert-${alert} alert-dismissible fade show" role="alert" style="line-height:15px;">
      <small>${message}</small>
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  `
}

function showStreamAlert(message, alert) {
  alertStream_wrapper.innerHTML = `
    <div id="alertStream" class="alert alert-${alert} alert-dismissible fade show" role="alert">
      <small>${message}</small>
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  `
}

// Function to set Analytic
function ai_stream_selectAnalytic() {
  if (analyticStream_selected.value=="analytic_none") {
    showVideoAlert("Seleccione la analítica", "warning")
    return;
  }
  else {
    // Set value to the analytic control
    if (analyticStream_selected.value=="analytic_detectO"){
      objectStream_selected.value = "all"
      objectStream_selected.disabled = False;
    }
    if (analyticStream_selected.value=="analytic_searchO"){
      objectStream_selected.value = "persona";
      objectStream_selected.disabled = False;
    }
    if (analyticStream_selected.value=="analytic_loiterP" || analyticStream_selected.value=="analytic_countP"){
      objectStream_selected.value = "persona";
      objectStream_selected.disabled = True;
    }
  }
}

// Function to set Object
function ai_stream_selectObject() {
  if (objectStream_selected.value=="none") {
    showStreamAlert("Seleccione el objeto", "warning")
    return;
  }
}

// Function to set Analytic
function ai_video_selectAnalytic() {
  if (analyticVideo_selected.value=="analytic_none") {
    showVideoAlert("Seleccione la analítica", "warning")
    return;
  }
  else {
    // Set value to the analytic control
    if (analyticVideo_selected.value=="analytic_detectO"){
      objectVideo_selected.value = "all"
    }
    // if (analyticVideo_selected.value=="analytic_searchO"){
    //   objectVideo_selected.value = "none"
    //   objectVideo_selected.disabled = false;
    // }
    if (analyticVideo_selected.value=="analytic_loiterP" || analyticVideo_selected.value=="analytic_countP" || analyticVideo_selected.value=="analytic_searchO"){
      objectVideo_selected.value = "persona"
      objectVideo_selected.disabled = false;
    }
  }
}

// Function to set Object
function ai_video_selectObject() {
  if (objectVideo_selected.value=="none") {
    showVideoAlert("Seleccione el objeto", "warning")
    return;
  }
}

// Function to upload file
function clicVideoProcess(url) {
  // Hide the Cancel button
  cancelVideo_btn.classList.add("d-none");
  // Hide the Process button
  processVideo_btn.classList.add("d-none");
  // Clear any existing alerts
  alertVideo_wrapper.innerHTML = "";
  // Show the load icon Process
  processVideo_wrapper.classList.remove("d-none");
}

// Function to stream
function ai_streamVideo(url) {

  // Reject if the file video is empty & throw alert
  if (camera_selected.value=="cam_none") {
    showVideoAlert("Debe seleccionar un video", "warning")
    return;
  }
  if (analyticStream_selected.value=="analytic_none") {
    showVideoAlert("Debe seleccionar una analítica", "warning")
    return;
  }
  if (objectStream_selected.value=="none") {
    showVideoAlert("Debe seleccionar un objeto", "warning")
    return;
  }
}

// Function to upload file ANALYTIC
function ai_analytic_uploadVideo(url) {

  // Reject if the file video is empty & throw alert
  if (!inputVideo.value) {
    showVideoAlert("Debe seleccionar un video", "warning")
    return;
  }
  if (analyticVideo_selected.value=="analytic_none") {
    showVideoAlert("Debe seleccionar una analítica", "warning")
    return;
  }
  if (objectVideo_selected.value=="none") {
    showVideoAlert("Debe seleccionar un objeto", "warning")
    return;
  }

  // Create a new FormData instance
  var data = new FormData();
  // Create a XMLHTTPRequest instance
  var request = new XMLHttpRequest();

  // Set the response type
  request.responseType = "json";
  // Clear any existing alerts
  alertVideo_wrapper.innerHTML = "";
  // Disable the input during upload
  inputVideo.disabled = true;
  // Hide the upload button
  uploadVideo_btn.classList.add("d-none");
  // Show the loading button
  loadingVideo_btn.classList.remove("d-none");
  // Show the cancel button
  cancelupVideo_btn.classList.remove("d-none");
  // Show the progress bar
  progressVideo_wrapper.classList.remove("d-none");

  // Get a reference to the file
  var file = inputVideo.files[0];
  // Get a reference to the filesize & set a cookie
  var filesize = file.size;
  var process = "video";

  document.cookie = `filesize=${filesize}`;
  // Append the file to the FormData instance
  data.append("file", file);
  // Append identifier of process VIDEO on media value
  data.append("process", process);

  if (analyticVideo_selected.value!="") {
    data.append("analytic", analyticVideo_selected.value);
  }
  if (objectVideo_selected.value!="") {
    data.append("object", objectVideo_selected.value);
  }

  // request progress handler
  request.upload.addEventListener("progress", function (e) {

    // Get the loaded amount and total filesize (bytes)
    var loaded = e.loaded;
    var total = e.total
    // Calculate percent uploaded
    var percent_complete = (loaded / total) * 100;

    // Update the progress text and progress bar
    progressVideo.setAttribute("style", `width: ${Math.floor(percent_complete)}%`);
    progressVideo_status.innerText = `${Math.floor(percent_complete)}% uploaded`;

  })

  // request load handler (transfer complete)
  request.addEventListener("load", function (e) {
    if (request.status == 200) {
      showVideoAlert(`${request.response.message}`, "success");
      reset_VideoUpload();
      // Disable the analytic control
      analyticVideo_selected.disabled = true;
      // Disable the object control
      objectVideo_selected.disabled = true;
      // Disable the input during upload
      inputVideo.disabled = true;
      // Hide the upload button
      uploadVideo_btn.classList.add("d-none");
      // Show the cancel button
      cancelVideo_btn.classList.remove("d-none");
      // Show the process button
      processVideo_btn.classList.remove("d-none");
    }
    else {
      showVideoAlert(`Error cargando archivo`, "danger");
      reset_VideoUpload();
    }
    
  });

  // request error handler
  request.addEventListener("error", function (e) {
    reset_VideoUpload();
    showVideoAlert(`Error cargando el video`, "warning");
  });

  // request abort handler
  request.addEventListener("abort", function (e) {
    reset_VideoUpload();
    showVideoAlert(`Carga cancelada`, "primary");
  });

  // Open and send the request
  request.open("POST", url);
  request.send(data);

  cancelupVideo_btn.addEventListener("click", function () {
    request.abort();
  })

}

// Function to upload file MASK
function ai_mask_uploadVideo(url) {

  // Reject if the file video is empty & throw alert
  if (!inputVideo.value) {
    showVideoAlert("Debe seleccionar un video", "warning")
    return;
  }
  // if (analyticVideo_selected.value=="analytic_none") {
  //   showVideoAlert("Debe seleccionar una analítica", "warning")
  //   return;
  // }

  // Create a new FormData instance
  var data = new FormData();
  // Create a XMLHTTPRequest instance
  var request = new XMLHttpRequest();

  // Set the response type
  request.responseType = "json";
  // Clear any existing alerts
  alertVideo_wrapper.innerHTML = "";
  // Disable the input during upload
  inputVideo.disabled = true;
  // Hide the upload button
  uploadVideo_btn.classList.add("d-none");
  // Show the loading button
  loadingVideo_btn.classList.remove("d-none");
  // Show the cancel button
  cancelupVideo_btn.classList.remove("d-none");
  // Show the progress bar
  progressVideo_wrapper.classList.remove("d-none");

  // Get a reference to the file
  var file = inputVideo.files[0];
  // Get a reference to the filesize & set a cookie
  var filesize = file.size;
  var process = "video";

  document.cookie = `filesize=${filesize}`;
  // Append the file to the FormData instance
  data.append("file", file);
  // Append identifier of process VIDEO on media value
  data.append("process", process);

  // if (analyticVideo_selected.value!="") {
  //   data.append("analytic", analyticVideo_selected.value);
  // }

  // request progress handler
  request.upload.addEventListener("progress", function (e) {

    // Get the loaded amount and total filesize (bytes)
    var loaded = e.loaded;
    var total = e.total
    // Calculate percent uploaded
    var percent_complete = (loaded / total) * 100;

    // Update the progress text and progress bar
    progressVideo.setAttribute("style", `width: ${Math.floor(percent_complete)}%`);
    progressVideo_status.innerText = `${Math.floor(percent_complete)}% uploaded`;

  })

  // request load handler (transfer complete)
  request.addEventListener("load", function (e) {
    if (request.status == 200) {
      showVideoAlert(`${request.response.message}`, "success");
      reset_VideoUpload();
      // Disable the analytic control
      // analyticVideo_selected.disabled = true;
      // Disable the input during upload
      inputVideo.disabled = true;
      // Hide the upload button
      uploadVideo_btn.classList.add("d-none");
      // Show the cancel button
      cancelVideo_btn.classList.remove("d-none");
      // Show the process button
      processVideo_btn.classList.remove("d-none");
    }
    else {
      showVideoAlert(`Error cargando archivo`, "danger");
      reset_VideoUpload();
    }
    
  });

  // request error handler
  request.addEventListener("error", function (e) {
    reset_VideoUpload();
    showVideoAlert(`Error cargando el video`, "warning");
  });

  // request abort handler
  request.addEventListener("abort", function (e) {
    reset_VideoUpload();
    showVideoAlert(`Carga cancelada`, "primary");
  });

  // Open and send the request
  request.open("POST", url);
  request.send(data);

  cancelupVideo_btn.addEventListener("click", function () {
    request.abort();
  })

}

cancelVideo_btn.addEventListener("click", function () {
    reset_VideoStart();
  })

// Function to update the input placeholder
function input_video_file() {
  file_video_label.innerText = inputVideo.files[0].name;
}

// Function to reset the upload
function reset_VideoUpload() {
  // Hide the cancel button
  cancelupVideo_btn.classList.add("d-none");
  // Reset the input video element
  inputVideo.disabled = false;
  // Show the upload button
  uploadVideo_btn.classList.remove("d-none");
  // Hide the loading button
  loadingVideo_btn.classList.add("d-none");
  // Hide the progress bar
  progressVideo_wrapper.classList.add("d-none");
  // Reset the progress bar state
  progressVideo.setAttribute("style", `width: 0%`);
}

// Function to reset the page
function reset_VideoStart() {
  // Clear the input
  inputVideo.value = null;
  inputVideo.disabled = false;
  // Reset the input placeholder
  file_video_label.innerText = "Seleccionar archivo";
  // Hide the cancel button
  cancelVideo_btn.classList.add("d-none");
  // Hide the process button
  processVideo_btn.classList.add("d-none");
  // Hide the alertVideo_wrapper alert
  alertVideo_wrapper.innerHTML = ``
  // Show the upload button
  uploadVideo_btn.classList.remove("d-none");
}