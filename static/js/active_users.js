const af_socket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/friend/active-friends/'
);     

af_socket.onopen = function() {
    console.log('AF WebSocket connection opened.')
}

af_socket.onmessage = function (event) {
    const af_data = JSON.parse(event.data);
    const userId = af_data.user_id; 
    const eventTrigger = af_data.trigger;
    
    if (eventTrigger === "ActiveUser") {
        if (af_data.is_active == true) {
            // handle online-friend sidebar
            const userLoggedIn = document.getElementById(`friend-${userId}`);
            userLoggedIn.style.display = 'inline';

            // handle the online-friends page
            const onlineFriendsPage = document.getElementById('online-friends-page');
            if (onlineFriendsPage) {
                const onlineFriendsData = [
                    { id: af_data.user_id, profile_photo: af_data.profile_photo, user_name: af_data.user_name},
                ];
                const pageTarget = "online-friends-page";
                addOnlineFriendsToList(onlineFriendsData, pageTarget);
            }
        }
        else {
            // handle the online sidebar for logouts
            const userLoggedIn = document.getElementById(`friend-${userId}`);
            userLoggedIn.style.display = 'none';
            // handle the online page for logouts
            const onlineFriendsPage = document.getElementById('online-friends-page');
            if (onlineFriendsPage) {
                const userOffline = document.getElementById(`friend-${userId}-page-item`);
                userOffline.remove();
            }
        }
    }
    else if (eventTrigger === "Friendship") {

        const onlineFriendsData = [
            { id: af_data.user_id, profile_photo: af_data.profile_photo, user_name: af_data.user_name},
        ];
        if (af_data.is_active == true) {
            const pageTarget = "sidebar&online-friends-page";
            addOnlineFriendsToList(onlineFriendsData, pageTarget);
        }
        else if (af_data.is_active == false){ 
            const userLoggedOutSidebar = document.getElementById(`friend-${userId}`);
            const userLoggedOutPage = document.getElementById(`friend-${userId}-page-item`);
            if (userLoggedOutSidebar) {
                userLoggedOutSidebar.style.display = 'none';
            }
            if (userLoggedOutPage) {
                userLoggedOutPage.style.display = 'none';
            }
        }
    }
};

fetch('/friend/online-friends/')
.then(response => response.json())
.then(data => {
    // Set the initial count from the server
    const activeUsers = data.active_users;
    for (const userId in activeUsers) {
        // display name with indicator
        const userLoggedIn = document.getElementById(`friend-${userId}`);
        userLoggedIn.style.display = 'inline';
    }
}); 

// Function to create a friend list item
function createFriendListItem(friend, page) {
    if (page === "sidebar") {
        const listItem = document.createElement('li');
        listItem.className = 'online-friends';
        listItem.id = `friend-${friend.id}`;
    
        const link = document.createElement('a');
        link.href = `/chat/dm/${friend.id}`;
        link.className = 'box-user-container';
    
        const profilePicture = document.createElement('img');
        profilePicture.className = 'mini-profile-picture';
        profilePicture.src = friend.profile_photo || '/media/app/default-user.png';
        profilePicture.alt = '...';
    
        profilePicture.style.height = '20px';
        profilePicture.style.width = '20px';
        profilePicture.style.marginRight = '0px';
    
        const onlineIndicator = document.createElement('span');
        onlineIndicator.className = 'online-indicator';
    
        onlineIndicator.style.marginLeft = "-10px";
    
        const friendName = document.createElement('small');
        friendName.id = `friend-name-${friend.id}`;
        friendName.textContent = `${friend.user_name}`;
    
        link.appendChild(profilePicture);
        link.appendChild(onlineIndicator);
        link.appendChild(friendName);
    
        listItem.appendChild(link);
    
        return listItem;
    }

    else if (page === "online-friends-page") {
        const firstFriendOnline = document.getElementById("no-online-friends");
        if (firstFriendOnline) {
            firstFriendOnline.style.display = 'none';
            const onlineFriendsForm = document.querySelector(".online-friends-form");
            onlineFriendsForm.style.display = 'block';
        }
        const listItem = document.createElement('li');
        listItem.className = 'online-friends-page';
        listItem.id = `friend-${friend.id}-page-item`;
    
        const link = document.createElement('a');
        link.href = `/chat/dm/${friend.id}`;
        link.className = 'box-user-container';
    
        const profilePicture = document.createElement('img');
        profilePicture.className = 'mini-profile-picture';
        profilePicture.src = friend.profile_photo || '/media/app/default-user.png';
        profilePicture.alt = '...';
    
        profilePicture.style.height = '20px';
        profilePicture.style.width = '20px';
        profilePicture.style.marginRight = '0px';
    
        const onlineIndicator = document.createElement('span');
        onlineIndicator.className = 'online-indicator';
    
        onlineIndicator.style.marginLeft = "-10px";
    
        const friendName = document.createElement('small');
        friendName.id = `friend-name-${friend.id}-page-item`;
        friendName.textContent = `${friend.user_name}`;
    
        link.appendChild(profilePicture);
        link.appendChild(onlineIndicator);
        link.appendChild(friendName);
    
        listItem.appendChild(link);
    
        return listItem;
    }
}

// Function to add online friends to the list
function addOnlineFriendsToList(friends, page) {
    let onlineFriendsList = null;
    let onlineFriendsPage = null;
    if (page === "sidebar") {
        onlineFriendsList = document.getElementById('online-friends-list');
    }
    else if (page === "online-friends-page") {
        onlineFriendsPage = document.getElementById('online-friends-page');
    }
    else if(page === "sidebar&online-friends-page") {
        onlineFriendsList = document.getElementById('online-friends-list');
        onlineFriendsPage = document.getElementById('online-friends-page');
    }

    friends.forEach(friend => {
        if (onlineFriendsList) {
            const page = "sidebar";
            const listItem = createFriendListItem(friend, page);
            onlineFriendsList.appendChild(listItem);
        }
        if (onlineFriendsPage) {
            const page = "online-friends-page";
            const listItem = createFriendListItem(friend, page);
            onlineFriendsPage.appendChild(listItem);
        }
    });
}