// Get room and user name
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const userName = JSON.parse(document.getElementById('user-name').textContent);

// Define chatsocket
const chatSocket = new WebSocket(
	'ws://'
	+ window.location.host
	+ '/ws/lounge/'
	+ roomName
	+ '/'
);

// Recieve message
chatSocket.onmessage = function (e) {
	// Get data
	const data = JSON.parse(e.data);

	// Check whether user is near bottom
	var bottom = (window.innerHeight + window.scrollY) >= (document.body.offsetHeight - 500) ? true : false;

	// Create message
	var container = document.createElement("div");
	var message = document.createElement("div");
	var message_text = document.createTextNode(data.message);

	// Add classes
	container.className += data.user != userName ? "message-container left" : "message-container right";
	message.className += "message";

	// Create final message
	container.appendChild(message).appendChild(message_text);

	// Add username to message if not own
	if (data.user != userName) {
		var sender = document.createElement("div");
		var sender_text = document.createTextNode(data.user);
		sender.className += "message-sender";
		container.appendChild(sender).appendChild(sender_text);
	}

	// Add message to chatbox
	document.querySelector('#chatbox').appendChild(container);

	// If near the bottom or has posted a message, scroll to bottom
	if (bottom || data.user == userName) {
		$("html, body").animate({ scrollTop: document.body.scrollHeight }, "slow");
	}

	// Hide message after 1 minute
	setTimeout(function () {
		$(container).hide("slow", function () {
			container.remove();
		});
	}, 60000);
};

// Close socket
chatSocket.onclose = function (e) {
	console.error('Chat socket closed unexpectedly');
};

// Send message
function sendMessage(event) {
	event.preventDefault();
	const messageInputDom = document.querySelector('#chat-message-input');
	const message = messageInputDom.value;
	chatSocket.send(JSON.stringify({
		'message': message,
		'user': userName
	}));
	messageInputDom.value = '';
};


// General scripts
$(function () {
	// Initialize page
	messageBoxElevation();

	// On scroll...
	$(window).on("scroll", function () {
		messageBoxElevation();
	});
});


// Message box shadow 
function messageBoxElevation() {
	var distance = $("#chatbox-container").offset().top + $("#chatbox-container").innerHeight() - window.pageYOffset;
	if (distance > ($(window).height() - 20)) {
		$("#chat-message-bar")
		.css("width", "90%")
		.css("padding", "0.5em")
		.css("box-shadow", "0 0 3px 3px rgb(0,0,0,0.1)");
	} else {
		$("#chat-message-bar")
		.css("width", "100%")
		.css("padding", "0")
		.css("box-shadow", "none");
	}
}

// Find lounge
function findLounge(event) {
	event.preventDefault();
	var roomName = document.querySelector('#room-name-input').value;
	window.location.pathname = '/lounges/' + roomName + '/';
}