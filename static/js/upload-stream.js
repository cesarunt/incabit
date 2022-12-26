// Get a reference to the 3 controls
var cameraStream_select = document.getElementById("cameraStream_select");
var imageTab   = document.getElementById("image-tab");
var videoTab   = document.getElementById("video-tab");
var streamTab  = document.getElementById("stream-tab");

// Function to upload file
function ai_mask_titleStream() {
  // Reset the input element
  cameraStream_select.disabled = true;
  imageTab.disabled = true;
  videoTab.disabled = true;
  // streamTab.disabled = true;
}