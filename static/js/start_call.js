let handleCall = async (user) => {
    const call = document.getElementById("call-data")
    const callerName = call.getAttribute("caller-name")

    let calleeData = await startCall();
    if (calleeData.callee_reachable) {
        let callee_id = calleeData.callee_id;
        let channel_name = calleeData.channel_name;
    
        let response = await fetch(`/call/generate-token/?channel=${channel_name}`);
        let callerData = await response.json();
    
        let UID = callerData.uid;
        let token = callerData.token;
        let name = callerName;
        let calling = true;
    
        sessionStorage.setItem('UID', UID);
        sessionStorage.setItem('CALLEEID', callee_id);
        sessionStorage.setItem('token', token);
        sessionStorage.setItem('channel', channel_name);
        sessionStorage.setItem('name', name);
        sessionStorage.setItem('CALLING', calling);
    
        window.open(`/call/call-room/${callee_id}`, "_self");    
    }
    else {
        console.log("user already on a call");
        notificationMessage = `${calleeData.callee_name} is already on a call.`;
        triggererProfilePhoto = calleeData.callee_photo; 
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

        imgElement.src = profilePhoto;
        imgElement.alt = 'Profile Photo';
        imgElement.style.width = '30px';
        imgElement.style.borderRadius = '50%';
        notificationMessageDiv.classList.add('box-user-container');
        notificationMessageDiv.id = 'existing-notification';
        message.style.marginLeft = '20px';
        message.textContent = notificationMessage;

        notificationMessageDiv.appendChild(imgElement);
        notificationMessageDiv.appendChild(message);
        modalContent.appendChild(notificationMessageDiv);

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
}

document.querySelectorAll(".start-call").forEach(button => {
    button.addEventListener("click", () => handleCall(button.closest(".user")));
});

let startCall = async () => {
    const call = document.getElementById("call-data")
    const callerName = call.getAttribute("caller-name")
    const callerId = call.getAttribute("caller-id")
    const calleeName = call.getAttribute("callee-name")
    const calleeId = call.getAttribute("callee-id")

    let response = await fetch('/call/start-call/', {
        method:'POST',
        headers: {
            'Content-Type':'application/json'
        },
        body:JSON.stringify({
            'caller_name': callerName, 
            'caller_id': callerId, 
            'callee_name': calleeName, 
            'callee_id': calleeId
        })
    });
    let data = await response.json()
    return data    
};
