import { declinedCallSocket } from "./decline_call_socket.js";
import { shownSenders, shownRooms } from "./track_senders.js";

document.addEventListener('DOMContentLoaded', function() {

    const PostSocket = new WebSocket(
        'ws://' 
        + window.location.host 
        + '/ws/notification/posts/'
    );

    const newFriendsocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/notification/new-friends/'
    );  

    const directMessageSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/notification/direct-messages/'
    );    

    const groupChatSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/notification/group-messages/'
    );    

    const friendRequestSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/notification/friend-requests/'
    );  

    const callSocket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/notification/calls/'
    );  

    // Handle the WebSocket connection when it opens 
    PostSocket.onopen = function () {
        console.log('PI WebSocket connection opened.');
    };

    directMessageSocket.onopen = function() {
        console.log('DM WebSocket connection opened.')
    };

    groupChatSocket.onopen = function() {
        console.log('GC WebSocket connection opened.')
    };

    friendRequestSocket.onopen = function() {
        console.log('FR WebSocket connection opened.')
    };

    newFriendsocket.onopen = function() {
        console.log('NF WebSocket connection opened.')
    };

    callSocket.onopen = function() {
        console.log('SC WebSocket connection opened.')
    };

    declinedCallSocket.onopen = function() {
        console.log('DC WebSocket connection opened.')
    };

    // Loading notifications from server when landing on pages
    const notificationCount = document.getElementById('notification-count');
    
    // Fetch the initial unread notification count from the server
    fetch('/notification/unread-notification-count/')
    .then(response => response.json())
    .then(data => {
        // Set the initial count from the server
        notificationCount.textContent = data.unread_notification_count + data.unread_newfriend_count;
        // Update the display based on the count
        if (data.unread_notification_count + data.unread_newfriend_count > 0) {
            notificationCount.style.display = 'block'; // Display the red bubble
        } else {
            notificationCount.style.display = 'none'; // Hide the red bubble when count is 0
        }
    });

    const messageCount = document.getElementById('message-count');
    
    fetch('/notification/unread-message-count/')
    .then(response => response.json())
    .then(data => {
        messageCount.textContent = data.unread_message_count;
    
        if (data.unread_message_count > 0) {
            messageCount.style.display = 'block'; 
        } else {
            messageCount.style.display = 'none'; 
        }
    });

    const groupMessageCount = document.getElementById('group-message-count');
    
    fetch('/notification/unread-group-message-count/')
    .then(response => response.json())
    .then(data => {
        groupMessageCount.textContent = data.unread_group_message_count;
    
        if (data.unread_group_message_count > 0) {
            groupMessageCount.style.display = 'block'; 
        } else {
            groupMessageCount.style.display = 'none'; 
        }
    });
      
    const FriendRequestCount = document.getElementById('friend-request-count');

    fetch('/friend/unread-friend-request-count/') 
    .then(response => response.json())
    .then(data => {
        FriendRequestCount.textContent = data.friend_request_count; 

        if (data.friend_request_count > 0) {
            FriendRequestCount.style.display = 'block'; 
        } else {
            FriendRequestCount.style.display = 'none'; 
        }
    });

    const missedCallsCount = document.getElementById('missed-calls-count');
    
    fetch('/notification/missed-calls-count/') 
    .then(response => response.json())
    .then(data => {
        missedCallsCount.textContent = data.missed_calls_count; 

        if (data.missed_calls_count > 0) {
            missedCallsCount.style.display = 'block'; 
        } else {
            missedCallsCount.style.display = 'none'; 
        }
    });

    // Handle incoming WebSocket messages
    PostSocket.onmessage = function (event) {
        const piData = JSON.parse(event.data);
        const piNotification = piData.notification;
        const piSender = piNotification.sender;
        const piSenderPhoto = piNotification.profile_photo;
        const piNotificationType = piNotification.notification_type;

        // Update the notification count
        const newNotificationCount = parseInt(notificationCount.textContent) + 1;
        notificationCount.textContent = newNotificationCount;
        if (newNotificationCount > 0) {
            notificationCount.style.display = 'block'; // Display the red bubble

            const url = `/notification/user-notifications/`;
            if (piNotificationType === 'Like') {
                const message = `${piSender} liked your post`;    
                showModal(message, piSenderPhoto, url);
            } else if (piNotificationType === 'Comment') {
                const message = `${piSender} commented on your post`;    
                showModal(message, piSenderPhoto, url);
            }

        } else {
            notificationCount.style.display = 'none'; // Hide the red bubble when count is 0
        }
    };

    directMessageSocket.onmessage = function (event) {
        const dmData = JSON.parse(event.data);
        const dmNotification = dmData.notification;
        const dmSender = dmNotification.sender;
        const dmSenderPhoto = dmNotification.profile_photo;
        const action = dmNotification.action;
        const dmSenderId = dmNotification.sender_id;

        if (action == "check"){
            const currentPath = window.location.pathname;

            directMessageSocket.send(JSON.stringify({
                "notification": dmNotification,
                "sender": dmSender,
                "sender_id": dmSenderId,
                "profile_photo": dmSenderPhoto,
                "current_path": currentPath
            }));
        }

        if (action == "notification"){
            const url = `/chat/dm/${dmSenderId}/`;
            const message = `New direct message from ${dmSender}`;
            showModal(message, dmSenderPhoto, url);

            // Check if the sender has already been shown
            if (!shownSenders.has(dmSenderId)) {
                const newMessageCount = parseInt(messageCount.textContent) + 1;
                messageCount.textContent = newMessageCount;
                
                if (newMessageCount > 0) {
                    messageCount.style.display = 'block';                 
                    // Add the sender to the Set to mark it as shown
                    shownSenders.add(dmSenderId);
                    // Update local storage
                    localStorage.setItem('shownSenders', JSON.stringify([...shownSenders]));
                } else {
                    messageCount.style.display = 'none'; 
                }
            }
        }
    };

    groupChatSocket.onmessage = function (event) {
        const gcData = JSON.parse(event.data);
        const gcNotification = gcData.notification;
        const gcRoomId = gcNotification.room_id;
        const gcSenderId = gcNotification.sender_id;
        const gcSender = gcNotification.sender;
        const gcSenderPhoto = gcNotification.profile_photo;
        const action = gcNotification.action;

        if (action == "check"){
            const currentPath = window.location.pathname;

            groupChatSocket.send(JSON.stringify({
                "notification": gcNotification,
                "room_id": gcRoomId,
                "sender": gcSender,
                "sender_id": gcSenderId,
                "profile_photo": gcSenderPhoto,
                "current_path": currentPath
            }));
        }

        if (action == "notification") {
            const url = `/chat/room/${gcRoomId}/`;
            const message = `New group message from ${gcSender}`;
            showModal(message, gcSenderPhoto, url);

            // Check if the room has already been shown
            if (!shownRooms.has(gcRoomId.toString())) {
                const newGroupMessageCount = parseInt(groupMessageCount.textContent) + 1;
                groupMessageCount.textContent = newGroupMessageCount;

                if (newGroupMessageCount > 0) {
                    groupMessageCount.style.display = 'block';                     
                    // Add the room to the Set to mark it as shown
                    shownRooms.add(gcRoomId.toString());
                    // Update local storage
                    localStorage.setItem('shownRooms', JSON.stringify([...shownRooms]));
                } else {
                    groupMessageCount.style.display = 'none'; 
                }
            }
        }
    };

    friendRequestSocket.onmessage = function (event) {
        const frData = JSON.parse(event.data);
        const frNotification = frData.notification;
        const frSender = frNotification.sender;
        const frSenderPhoto = frNotification.profile_photo;

        const newFriendRequestCount = parseInt(FriendRequestCount.textContent) + 1; 
        FriendRequestCount.textContent = newFriendRequestCount;

        if (newFriendRequestCount > 0) {
            FriendRequestCount.style.display = 'block'; 

            const url = `/friend/friend-requests/`;
            const message = `${frSender} sent you a friend request`;
            showModal(message, frSenderPhoto, url);
        } else {
            FriendRequestCount.style.display = 'none'; 
        }
    };

    newFriendsocket.onmessage = function (event) {
        const nfData = JSON.parse(event.data);
        const nfNotification = nfData.notification;
        const nfSender = nfNotification.sender;
        const nfSenderPhoto = nfNotification.profile_photo;

        const newNotificationCount = parseInt(notificationCount.textContent) + 1;
        notificationCount.textContent = newNotificationCount;

        if (newNotificationCount > 0) {
            notificationCount.style.display = 'block'; 

            const url = `/notification/user-notifications/`;
            const message = `${nfSender} accepted your friend request`;
            showModal(message, nfSenderPhoto, url);
        } else {
            notificationCount.style.display = 'none';
        }  
    };

    callSocket.onmessage = function (event) {
        const callData = JSON.parse(event.data);
        const callNotification = callData.notification;
        const callNotificationType = callNotification.notification_type;

        if (callNotificationType === 'call') {
            // Sent from signal
            const callerId = callNotification.caller_id;
            const calleeId = callNotification.callee_id;
            const caller = callNotification.caller;
            const callee = callNotification.callee;
            const callerPhoto = callNotification.profile_photo;
            const channelName = callNotification.channel_name;
    
            fetch(`/call/generate-token/?channel=${channelName}`)
            .then((response) => {
                return response.json();
            })
            .then((data) => {
                let UID = data.uid; 
                let token = data.token;
                sessionStorage.setItem('UID', UID);
                sessionStorage.setItem('token', token);
            })
            .catch((error) => {
                console.error('Error fetching data:', error);
            });
    
            const calling = false;
    
            sessionStorage.setItem('CALLEEID', calleeId);
            sessionStorage.setItem('channel', channelName);
            sessionStorage.setItem('name', callee);
            sessionStorage.setItem('CALLING', calling);
            
            const message = `Incomming call from ${caller}`;
            const answerUrl = `/call/call-room/${callerId}`;
    
            showCallModal(message, callerPhoto, answerUrl, callerId);
        } else if (callNotificationType === 'missed-call') {
            // Sent from consumer's receive method 
            const callerId = callNotification.caller_id;
            const callerName = callNotification.caller_name;
            const callerPhoto = callNotification.caller_photo;
    
            const newMissedCallsCount = parseInt(missedCallsCount.textContent) + 1;
            missedCallsCount.textContent = newMissedCallsCount;
    
            if (newMissedCallsCount > 0) {
                missedCallsCount.style.display = 'block'; 
                const url = `/call/calls-history/`;
                const message = `You missed ${callerName}'s call`;
                showModal(message, callerPhoto, url);
            } else {
                missedCallsCount.style.display = 'none';
            }      
        }
    };

    // Handle WebSocket closure
    PostSocket.onclose = function () {
        console.log('PI WebSocket connection closed.');
    };
    directMessageSocket.onclose = function () {
        console.log('DM WebSocket connection closed.');
    };
    groupChatSocket.onclose = function () {
        console.log('GC WebSocket connection closed.');
    };
    friendRequestSocket.onclose = function () {
        console.log('FR WebSocket connection closed.');
    };
    newFriendsocket.onclose = function () {
        console.log('NF WebSocket connection closed.');
    };   
    callSocket.onclose = function () {
        console.log('SC WebSocket connection closed.');
    };   
    declinedCallSocket.onclose = function () {
        console.log('DC WebSocket connection closed.');
    };   

    // Function to show the notification modal 
    function showModal(notificationMessage, triggererProfilePhoto, url) {
        const modalElement = document.getElementById("notification-modal-id");
        document.getElementById("notification-modal-id").style.display = "flex";
        let modalDurationTime = 3000;
        const existingNotification = document.getElementById("existing-notification");
        if (existingNotification) {
            existingNotification.remove();
            modalDurationTime += 3000;
        }
        const profilePhoto = triggererProfilePhoto[0] != null ? triggererProfilePhoto : '/media/app/default-user.png';
        const imgElement = document.createElement('img');
        const modalContent = document.getElementById("notification-modal-text");
        const notificationMessageDiv = document.createElement('div');
        const message = document.createElement('p');
        const NotificationLink = document.createElement('a');

        imgElement.src = profilePhoto;
        imgElement.alt = 'Profile Photo';
        imgElement.style.width = '30px';
        imgElement.style.borderRadius = '50%';
        notificationMessageDiv.classList.add('box-user-container');
        notificationMessageDiv.id = 'existing-notification';
        message.style.marginLeft = '20px';
        message.textContent = notificationMessage;
        NotificationLink.href = url;
        NotificationLink.classList.add('custom-link');

        notificationMessageDiv.appendChild(imgElement);
        notificationMessageDiv.appendChild(message);
        NotificationLink.appendChild(notificationMessageDiv);
        modalContent.appendChild(NotificationLink);

        // Clear any existing timeout for modal to last longer when a new notification arrives
        clearTimeout(modalElement.timeoutId);
        // Set a timeout to hide the notification modal after 3 seconds
        setTimeout(() => {
            // Remove modal content after 3 seconds
            notificationMessageDiv.remove();
            // Hide the modal after removing the content
            document.getElementById("notification-modal-id").style.display = "none";
        }, modalDurationTime);
    }

    function showCallModal(notificationMessage, triggererProfilePhoto, url, callerId) {
        let callDeclined = false;
        const modalElement = document.getElementById("call-modal-id");
        document.getElementById("call-modal-id").style.display = "flex";
        document.getElementById("call-modal-id").style.zIndex = "3";
        let modalDurationTime = 20000;
        const existingNotification = document.getElementById("existing-call");
        if (existingNotification) {
            existingNotification.remove();
        }
        const profilePhoto = triggererProfilePhoto[0] != null ? triggererProfilePhoto : '/media/app/default-user.png';
        const imgElement = document.createElement('img');
        const modalContent = document.getElementById("call-modal-text");
        const notificationMessageDiv = document.createElement('div');
        const message = document.createElement('p');
        const callLink = document.createElement('a');
        
        const answer = document.createElement('i');
        answer.innerHTML = `<i class="fa-solid fa-phone"></i>`;
        answer.style.color = '#fff';
        answer.style.fontSize = '20px';
        answer.style.marginRight = '20px';
        answer.style.padding = '20px';
        answer.style.border = 'green';
        answer.style.borderRadius = '50%';
        answer.style.backgroundColor = 'green';

        answer.addEventListener('mouseover', function() {
            answer.style.backgroundColor = '#8FED8F'; 
            decline.style.cursor = 'pointer';
        });
        
        answer.addEventListener('mouseout', function() {
            answer.style.backgroundColor = 'green';
        });

        const decline = document.createElement('i');
        decline.innerHTML = `<i class="fa-solid fa-x"></i>`;
        decline.style.color = '#fff';
        decline.style.fontSize = '20px';
        decline.style.marginRight = '20px';
        decline.style.padding = '20px';
        decline.style.border = 'red';
        decline.style.borderRadius = '50%';
        decline.style.backgroundColor = 'red';
        
        decline.addEventListener('mouseover', function() {
            decline.style.backgroundColor = '#FFB6C1'; 
            decline.style.cursor = 'pointer';
        });
        
        decline.addEventListener('mouseout', function() {
            decline.style.backgroundColor = 'red';
        });

        decline.addEventListener('click', function() {
            declinedCallSocket.send(JSON.stringify({
                "notification": {
                  "notification_type": "decline",
                  "caller_id": callerId
                }
            }));
            notificationMessageDiv.remove();
            document.getElementById("call-modal-id").style.display = "none";
            callDeclined = true;
        });

        const actionDiv = document.createElement("div");
        actionDiv.style.marginLeft = "30%";

        imgElement.src = profilePhoto;
        imgElement.alt = 'Profile Photo';
        imgElement.style.width = '60px';
        imgElement.style.borderRadius = '50%';
        notificationMessageDiv.classList.add('box-user-container');
        const callDiv = document.createElement("div");
        callDiv.id = 'existing-call';

        message.style.marginLeft = '20px';
        message.textContent = notificationMessage;
        callLink.href = url;
        callLink.classList.add('custom-link');

        notificationMessageDiv.appendChild(imgElement);
        notificationMessageDiv.appendChild(message);
        callLink.appendChild(answer);
        callDiv.appendChild(notificationMessageDiv);
        const breakLine = document.createElement("br");
        callDiv.appendChild(breakLine);
        actionDiv.appendChild(callLink);
        actionDiv.appendChild(decline);
        callDiv.appendChild(actionDiv);
        const breakLine2 = document.createElement("br");
        callDiv.appendChild(breakLine2);
        modalContent.appendChild(callDiv);

        clearTimeout(modalElement.timeoutId);
        
        setTimeout(() => {
            if (!callDeclined) {
                notificationMessageDiv.remove();
                document.getElementById("call-modal-id").style.display = "none";
                // missed call
                callSocket.send(JSON.stringify({
                    "notification": {
                        "notification_type": "missed-call",
                        "caller_photo": profilePhoto,
                        "caller_id": callerId
                    }
                }));
            }
        }, modalDurationTime);
    }

    // When the user clicks outside the modal, close it
    window.addEventListener("click", function (event) {
        if (event.target === document.getElementById("notification-modal-id")) {
            document.getElementById("notification-modal-id").style.display = "none";
        }
    });
});

