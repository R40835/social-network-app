const paginator = document.getElementById("messages-paginator");
let currentPage;
let totalPages;
let currentUserId;

if (paginator) {
    currentPage = parseInt(paginator.getAttribute("current-page"));
    totalPages = parseInt(paginator.getAttribute("total-pages"));
    currentUserId = paginator.getAttribute("current-user-id");
}
let loadingMessages = false;
let previousScrollHeight = document.getElementById('chat-log').scrollHeight;

function appendMessagesToChatLog(pageNumber) {
    // Show the loading spinner
    const loadingSpinner = document.getElementById('loading-spinner');
    loadingSpinner.style.display = 'block';

    // Fetch and append messages
    const nextPageUrl = `?page=${pageNumber}`;
    fetch(nextPageUrl)
        .then(response => response.text())
        .then(content => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(content, 'text/html');

            const messageContainers = doc.querySelectorAll('.message-container');

            const chatLog = document.getElementById('chat-log');
            const firstMessage = chatLog.querySelector('.message-container'); 

            // Insert messages from the current page
            messageContainers.forEach(messageContainer => {
                const senderId = messageContainer.getAttribute('sender'); 
                const senderIdentity = messageContainer.getAttribute('data-sender');
                const timestamp = messageContainer.getAttribute('data-timestamp');
                const messageContent = messageContainer.querySelector('p').innerHTML;
                const profilePhoto = messageContainer.querySelector('.participant-photo').outerHTML;

                // message's sender 
                const clonedSenderElement = document.createElement('small');
                clonedSenderElement.classList.add('sender-identity');
                clonedSenderElement.style.fontWeight = 'bold'; 
                clonedSenderElement.textContent = (senderId === currentUserId) ? "You" : senderIdentity;  
                clonedSenderElement.style.fontWeight = 'bold'

                // message's timestamp
                const clonedTimestampElement = document.createElement('small');
                clonedTimestampElement.style.marginLeft = '0.5em'; 
                clonedTimestampElement.textContent = timestamp;

                // Create a container to hold both elements
                const senderAndTimestampContainer = document.createElement('div');
                senderAndTimestampContainer.style.display = 'inline-block'; 

                // message's container
                const clonedMessageContainer = document.createElement('div');
                // Add class based on sender
                clonedMessageContainer.classList.add('message-container');
                if (senderId === currentUserId) {
                    clonedMessageContainer.classList.add('sender-message');
                } else {
                    clonedMessageContainer.classList.add('receiver-message');
                    senderAndTimestampContainer.style.marginLeft = '50%'; 
                }

                senderAndTimestampContainer.appendChild(clonedSenderElement);
                senderAndTimestampContainer.appendChild(clonedTimestampElement);
                clonedMessageContainer.innerHTML = profilePhoto + messageContent;

                // Append sender identity, message container, and timestamp elements
                chatLog.insertBefore(clonedMessageContainer, firstMessage);
                chatLog.insertBefore(senderAndTimestampContainer, firstMessage)
            });


            // Calculate the difference in scroll height and adjust the scroll position
            const newScrollHeight = chatLog.scrollHeight;
            const scrollDifference = newScrollHeight - previousScrollHeight;
            chatLog.scrollTop += scrollDifference;

            previousScrollHeight = newScrollHeight;

            loadingMessages = false;

            // Hide the loading spinner when messages are loaded
            loadingSpinner.style.display = 'none';
        })
        .catch(error => {
            console.error('Error:', error);
            loadingMessages = false;
        });
}

const chatLog2 = document.getElementById('chat-log');
chatLog2.addEventListener('scroll', function() {
    if (chatLog2.scrollTop === 0 && !loadingMessages && currentPage < totalPages) {
        loadingMessages = true;
        currentPage++;

        appendMessagesToChatLog(currentPage);
    }
});