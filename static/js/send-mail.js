// Get a reference to the elements
var mail_username = document.getElementById("mail_username");
var mail_address  = document.getElementById("mail_address");
var mail_message  = document.getElementById("mail_message");
var mail_phonenumber  = document.getElementById("mail_phonenumber");

var alertMail_wrapper = document.getElementById("alertMail_wrapper");
// var alertMailTop = document.getElementById("alertMailTop");
var sendMail_btn = document.getElementById("sendMail_btn");
var loadMail_img = document.getElementById("loadMail_img");

// Function to show alerts
function showMail_alert(message, add, alert) {
  alertMail_wrapper.innerHTML = `
    <div id="alertMail" class="alert alert-${alert} alert-dismissible fade show" role="alert">
      <span>${message} <b>${add}</b>.</span>
      <button type="button" class="close" data-dismiss="alert" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
  `  
}

// Function to upload file
function home_sendMail(url) {

  // Reject if the file input is empty & throw alert
  if (!mail_username.value || !mail_address.value || !mail_message.value || !mail_phonenumber.value) {
    showMail_alert("Debe completar los campos obligatorios","(*)", "warning")
    return;
  }

  // Create a new FormData instance
  var data = new FormData();
  // Create a XMLHTTPRequest instance
  var request = new XMLHttpRequest();

  // Set the response type
  request.responseType = "json";
  // Clear any existing alerts
  alertMail_wrapper.innerHTML = "";
  // Hide the sending button
  sendMail_btn.classList.add("d-none");
  // Show the loading button
  loadMail_img.classList.remove("d-none");

  data.append("mail_username", mail_username.value);
  data.append("mail_address" , mail_address.value);
  data.append("mail_message" , mail_message.value);
  data.append("mail_phonenumber" , mail_phonenumber.value);

  // request load handler (transfer complete)
  request.addEventListener("load", function (e) {
    if (request.status == 200) {
      showMail_alert(`${request.response.message}`, `${request.response.add}`, "success");
      // Hide the loading button
      loadMail_img.classList.add("d-none");
      // Show the sending button
      sendMail_btn.classList.remove("d-none");
      // Clear inputs
      mail_username.value = ""
      mail_address.value  = ""
      mail_phonenumber.value = ""
      mail_message.value = ""
    }
    else {
      showMail_alert(`Error enviando el mensaje`, "danger");
      reset_startMail();
    }
  });
  // Open and send the request
  request.open("POST", url);
  request.send(data);
}

// Function to reset the page
function reset_startMail() {
  // Show the upload button
  sendMail_btn.classList.remove("d-none");
  // Hide the loading button
  loadMail_img.classList.add("d-none");
  // Hide the alert_wrapper alert
  alertMail_wrapper.innerHTML = ``
}