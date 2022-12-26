<?php

function send_msg_whatsapp($number,$message){
	$data = [
		'phone'  => "51".$number,
		'message' =>  $message
		// "filename"  =>  $imagen,		// "attachment" =>  "data:image/jpeg;base64,$imagen"
	];
	
	$json = json_encode($data);	
	$curl = curl_init();
	
	curl_setopt_array($curl, array(
		CURLOPT_URL => 'https://www.visualsatpe.com:205/api/whatsapp/sendmessages/4',
		CURLOPT_RETURNTRANSFER => true,
		CURLOPT_ENCODING => '',
		CURLOPT_MAXREDIRS => 10,
		CURLOPT_TIMEOUT => 0,
		CURLOPT_FOLLOWLOCATION => true,
		CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
		CURLOPT_CUSTOMREQUEST => 'POST',
		CURLOPT_POSTFIELDS => $json,
		CURLOPT_HTTPHEADER => array(
		  'Authorization: hlmq7xyvxw8em8bx',
		  'Content-Type: application/json'
		),
	  ));
	
	$response = curl_exec($curl);
	curl_close($curl);
}

// Input Values
$number = "943002381";
$message = "ALERTA: INTRUSO DETECTADO";
send_msg_whatsapp($number, $message);

$image_name = $argv[1];
$message = "http://incabit.com:5000/".$image_name;
send_msg_whatsapp($number, $message);
?>