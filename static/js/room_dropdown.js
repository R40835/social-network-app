const roomMembers = document.querySelectorAll('[id^="member-"]')
roomMembers.forEach(function(roomMember) {
    const memberId = roomMember.getAttribute("member-id")
    // Fetch the room member from the server
    fetch('/chat/room-member/'+ memberId + '/')
    .then(response => response.json())
    .then(data => {
        const userName = data.member_name;
        const profilePhoto = data.member_profile_photo;
        const imgElement = document.createElement('img');
        const memeberInfoDiv = document.createElement('div');
        const userNameElement = document.createElement('p');
        
        imgElement.src = profilePhoto;
        userNameElement.textContent = userName;
        imgElement.alt = 'Profile Photo';
        imgElement.style.width = '20px';
        imgElement.style.borderRadius = '50%';
        memeberInfoDiv.classList.add('box-user-container');
        userNameElement.style.marginLeft = '5px';

        memeberInfoDiv.appendChild(imgElement);
        memeberInfoDiv.appendChild(userNameElement);
        roomMember.appendChild(memeberInfoDiv);
    });
});