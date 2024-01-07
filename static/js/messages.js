import { shownSenders, shownRooms } from "./track_senders.js";

let userId;
let roomId;
let chatSocket;

try {
    userId = JSON.parse(document.getElementById('user-id').textContent);
}
catch (error) {
    console.log("room messages.");
}
try {
    roomId = JSON.parse(document.getElementById('room-id').textContent);
}
catch (error) {
    console.log("direct messages.");
}
try {
    if (userId) {
        chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/dm/'
            + userId
            + '/'
        );
        // Show notifications for the sender in notifications.js 
        const shownSender = userId.toString();
        shownSenders.delete(shownSender);
        localStorage.setItem('shownSenders', JSON.stringify([...shownSenders]));
    }
    else if (roomId) {
        chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/room/'
            + roomId
            + '/'
        );
        // Show notifications for the room in notifications.js
        const shownRoom = roomId.toString();
        shownRooms.delete(shownRoom);
        localStorage.setItem('shownRooms', JSON.stringify([...shownRooms])); 
    }
} catch (error) {
    console.error('WebSocket connection error:', error);
}

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const chatLog = document.querySelector('#chat-log');
    const participantFullName = data.name;
    const senderId = data.sender_id;
    const participantFirstName = participantFullName.split(' ')[0];
    const timeStamp = data.timestamp;

    const currentUserId = parseInt(chatLog.getAttribute("current-user-id"));
    const currentUserProfilePhoto = chatLog.getAttribute("current-user-profile-photo");
    const participantProfilePhoto = chatLog.getAttribute("paticipant-profile-photo");
    
    // On first message sent
    try {
        var noMessages = document.getElementById("no-messages");
        if (noMessages != null) {

            if (noMessages.style.display !== "none") {
                noMessages.style.display = "none";
            } else {
                // The element with the specified ID does not exist
                console.log("Element with ID 'no-messages' does not exist.");
            }

        }
    } catch (error) {
        console.error("An error occurred:", error);
    }
    // Determine if the current user is the sender
    const isCurrentUser = (senderId === currentUserId);

    // Determine the appropriate CSS class based on the sender's identity
    const messageClass = isCurrentUser ? 'sender-message' : 'receiver-message';

    // Create a new message container element
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message-container', messageClass);

    // Getting sender's photo url using participantProfilePhoto for DMs, and PhotoUrlFromServer for Rooms
    let ParticipantphotoSrc;
    if (userId) {
        ParticipantphotoSrc = participantProfilePhoto;
    } else {
        let PhotoUrlFromServer = data.profile_photo != null ? data.profile_photo : '/media/app/default-user.png';
        ParticipantphotoSrc = PhotoUrlFromServer;
    }

    const UserPhotoSrc = currentUserProfilePhoto;
    // Create a new image element for the participant's profile photo
    const imgElement = document.createElement('img');
    imgElement.src = isCurrentUser ? UserPhotoSrc : ParticipantphotoSrc;
    imgElement.alt = 'Profile Image';
    imgElement.classList.add('participant-photo');

    // Create a new content element for the message text
    const contentElement = document.createElement('p');
    contentElement.textContent = data.message;

    // Display the participant's username above the message container
    const participantUsernameElement = document.createElement('small');
    participantUsernameElement.classList.add('participant-username');
    participantUsernameElement.textContent = isCurrentUser ? 'You' : participantFirstName;
    participantUsernameElement.style.fontWeight = 'bold';

    const timeStampElement = document.createElement('small');
    timeStampElement.classList.add('participant-username');
    timeStampElement.textContent = timeStamp;
    timeStampElement.style.marginLeft = '0.5em';
    
    const senderAndTimestampContainer = document.createElement('div');
    senderAndTimestampContainer.style.display = 'inline-block';
    senderAndTimestampContainer.appendChild(participantUsernameElement)
    senderAndTimestampContainer.appendChild(timeStampElement)

    if (!isCurrentUser) {
        senderAndTimestampContainer.style.marginLeft = '50%';
    }

    // Append the image and content elements to the message container
    messageContainer.appendChild(imgElement);
    messageContainer.appendChild(contentElement);

    // Append the new message container to the chat log
    chatLog.appendChild(messageContainer);

    // Append the sender's identity and participant's username elements to the chat log
    chatLog.appendChild(senderAndTimestampContainer)

    // changing indicator 
    var messageElement = document.getElementById("indicator");
    // Check the condition and update class and content accordingly
    if (isCurrentUser) {
        messageElement.className = "message-indicator sent-indicator"; // Change the class
        messageElement.textContent = "Sent";
        messageElement.style.display = 'block';
    }
    else {
        messageElement.className = "message-indicator received-indicator"; // Change the class
        messageElement.textContent = "Received"; 
        messageElement.style.display = 'block';
    }

    // Scroll to the bottom of the chat log
    chatLog.scrollTop = chatLog.scrollHeight;
};

//show last message
const chatLog = document.querySelector('#chat-log');
chatLog.scrollTop = chatLog.scrollHeight;

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#chat-message-input').focus();
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.key === 'Enter') {  
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    const messageInputDom = document.querySelector('#chat-message-input');
    const message = messageInputDom.value;
    // sending message to the consumer in the backend
    chatSocket.send(JSON.stringify({
        'message': message
    }));
    messageInputDom.value = '';
};

const submitButton = document.getElementById('submit-button'); // do not send blanks!