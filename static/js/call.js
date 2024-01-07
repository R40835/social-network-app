import { declinedCallSocket } from "./decline_call_socket.js";

const audio = document.getElementById("calling-tone");
const TOKEN = sessionStorage.getItem('token');
const CHANNEL = sessionStorage.getItem('channel');

let getApp = async () => {
    let response = await fetch(`/call/get-app/?channel_name=${CHANNEL}`); 
    let data = await response.json();
    return data; 
};

const AppData = await getApp();
const APP_ID = AppData.app_id;

let UID = sessionStorage.getItem('UID');
let CALLING = sessionStorage.getItem('CALLING');
let callAnswered = false;

declinedCallSocket.onmessage = async function (event) {
    const declinedCalldata = JSON.parse(event.data);
    const notificationData = declinedCalldata.notification;
    console.log("call declined: ", notificationData.caller_id);

    const notificationType = notificationData.notification_type;
    const callerId = notificationData.caller_id;

    if (callerId === UID && notificationType === "decline") { 
        audio.pause();
        CALLING = false;
        await showCallEndedModal('Call declined');
    }
}

const client = AgoraRTC.createClient({mode: 'rtc', codec: 'vp8'});

let localTracks = [];
let remoteUsers = {};

let joinAndDisplayLocalStream = async () => {
    client.on('user-published', handleUserJoined);
    client.on('user-left', handleUserLeft);

    try {
        UID = await client.join(APP_ID, CHANNEL, TOKEN, UID);
    } catch(error) {
        console.log(error);
        window.open('/', '_self');
    }
    
    localTracks = await AgoraRTC.createMicrophoneAndCameraTracks();

    await handleCurrentUserJoin();

    localTracks[1].play(`user-${UID}`);
    await client.publish([localTracks[0], localTracks[1]]);

    if (CALLING){
        audio.play();
        callTimeout();
    }
}

let handleUserJoined = async (user, mediaType) => {
    remoteUsers[user.uid] = user;
    await client.subscribe(user, mediaType);
    callAnswered = true;

    if (mediaType === 'video') {
        let player = document.getElementById(`user-container-${user.uid}`);
        if (player != null) {
            player.remove();
        }

        if (CALLING) {
            audio.pause();
            CALLING = false;
        }

        const awaitingResponseFrame = document.getElementById("awaiting-response");
        if (awaitingResponseFrame) {
            awaitingResponseFrame.remove();
        }

        await handleRemoteUserJoin(user);

        player = `<div  class="video-container" id="user-container-${user.uid}">
                    <div class="video-player" id="user-${user.uid}"></div>
                </div>`; 

        document.getElementById('video-streams').insertAdjacentHTML('beforeend', player);
        user.videoTrack.play(`user-${user.uid}`);
    }

    if (mediaType === 'audio') {
        user.audioTrack.play();
    }
}

let handleUserLeft = async (user) => {
    delete remoteUsers[user.uid];
    leaveAndRemoveLocalStream();
}

let leaveAndRemoveLocalStream = async () => { 
    for (let i=0; localTracks.length > i; i++) {
        localTracks[i].stop();
        localTracks[i].close();
    }

    await client.leave();
    await showCallEndedModal('Call ended');
    await HangUp();
}

let toggleCamera = async (e) => {
    const cameraOn = document.getElementById("camera-on-button");
    const cameraOff = document.getElementById("camera-off-button");

    if (localTracks[1].muted) {
        await localTracks[1].setMuted(false);
        cameraOn.style.display = "block";
        cameraOff.style.display = "none";    
    } else {
        await localTracks[1].setMuted(true);
        cameraOn.style.display = "none";
        cameraOff.style.display = "block";    
    }
}

let toggleMic = async (e) => {
    const micOn = document.getElementById("mic-on-button");
    const micOff = document.getElementById("mic-off-button");

    if (localTracks[0].muted) {
        await localTracks[0].setMuted(false);
        micOn.style.display = "block";
        micOff.style.display = "none";    
    } else {
        await localTracks[0].setMuted(true);
        micOn.style.display = "none";
        micOff.style.display = "block";    
    }
}

let handleCurrentUserJoin = async () => {
    let response = await fetch(`/call/current-user-join/?user_id=${UID}&channel_name=${CHANNEL}`); 
    let data = await response.json();
    return data.name ;
};

let handleRemoteUserJoin = async (user) => {
    let response = await fetch(`/call/remote-user-join/?user_id=${user.uid}&channel_name=${CHANNEL}`);
    let data = await response.json();
    return data.name;
};

let HangUp = async () => {
    let response = await fetch(`/call/hang-up/?user_id=${UID}&channel_name=${CHANNEL}`);
    let data = await response.json();
    console.log(`Call status: ${data.call_status}`);
};

const showCallEndedModal = async (callDeclinedMessage) => {
    const modalElement = document.getElementById("call-modal-id");
    document.getElementById("call-modal-id").style.display = "flex";
    document.getElementById("call-modal-id").style.zIndex = "3";

    const modalContent = document.getElementById("call-modal-text");
    const callMessageDiv = document.createElement('div');
    const message = document.createElement('p');

    callMessageDiv.classList.add('box-user-container');
    const callDiv = document.createElement("div");

    message.style.marginLeft = '20px';
    message.textContent = callDeclinedMessage;

    callMessageDiv.appendChild(message);
    callDiv.appendChild(callMessageDiv);
    modalContent.appendChild(callDiv);

    clearTimeout(modalElement.timeoutId);

    setTimeout(() => {
        callMessageDiv.remove();
        document.getElementById("call-modal-id").style.display = "none";
        window.open('/call/calls-history/', '_self');
    }, 3000);
};

// Check every second
const callTimeout = async () => {
    let startTime = Date.now(); // Record the start time in milliseconds
    let twentySecondsPassed = false;

    // Function to check if 20 seconds have passed
    const checkElapsedTime = async () => {
        const currentTime = Date.now();
        const elapsedTime = currentTime - startTime;

        if (callAnswered) {
            console.log("call answered");
        } else if (elapsedTime >= 20000 && !callAnswered) { // 20,000 milliseconds = 20 seconds
            twentySecondsPassed = true;
            console.log("20 seconds have passed!");
            showCallEndedModal("No answer");
        } else {
            // If 20 seconds have not passed, set another timeout for the next check
            await new Promise(resolve => setTimeout(resolve, 1000)); // Check every 1000 milliseconds = 1 second
            checkElapsedTime();
        }
    };
    // Initial call to start the timeout loop
    await checkElapsedTime();
};

window.addEventListener("beforeunload", HangUp);

joinAndDisplayLocalStream();

document.getElementById('hangup-wrapper').addEventListener('click', leaveAndRemoveLocalStream);
document.getElementById('camera-wrapper').addEventListener('click', toggleCamera);
document.getElementById('mic-wrapper').addEventListener('click', toggleMic);