document.addEventListener("DOMContentLoaded", function() {
    const container = document.querySelector('.infinite-container');
    const csrfToken = getCookie('csrftoken');

    container.addEventListener('click', function(event) {
        const target = event.target;
        if (target.classList.contains('action-button')) {
            const url = target.getAttribute("data-url");
            const userId = target.getAttribute("user-id");
            const action = target.getAttribute("button-action");

            if (target.classList.contains("add-friend-button")) {
                if (action === "accept") {
                    sendActionRequest(url);
                    target.classList.remove("add-friend-button");
                    target.classList.add("remove-friend-button");
                    target.textContent = "Remove";
 
                    var appPath = basePath + `friend/remove-send-cancel-request/${userId}`;
                    target.setAttribute("data-url", appPath);
                    target.setAttribute("button-action", "send-cancel");

                    const acceptButton = document.getElementById(`accept-button-${userId}`);
                    const declineButton = document.getElementById(`decline-button-${userId}`); 
                    const acceptedButton = document.getElementById(`accepted-button-${userId}`);

                    if (declineButton && declineButton.classList.contains("remove-friend-button")) {
                        declineButton.remove();
                        acceptButton.remove();
                        acceptedButton.style.display = 'block';
                    }
                }

            } else if (target.classList.contains("remove-friend-button")) {
                if (action === "decline") {
                    sendActionRequest(url);
                    target.classList.remove("remove-friend-button");
                    target.classList.add("add-friend-button");
                    target.textContent = "Add Friend";
                    var appPath = basePath + `friend/send-cancel-request/${userId}`;
                    target.setAttribute("data-url", appPath);
                    target.setAttribute("button-action", "send-cancel");

                    const declineButton = document.getElementById(`decline-button-${userId}`);
                    const acceptButton = document.getElementById(`accept-button-${userId}`);
                    const declinedButton = document.getElementById(`declined-button-${userId}`);

                    if (acceptButton && acceptButton.classList.contains("add-friend-button")) {
                        acceptButton.remove();
                        declineButton.remove();
                        declinedButton.style.display = 'block';
                        
                    }
                }
            }
        }
    });

    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }

    function sendActionRequest(url) {
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            console.log('Response from the server:', data.response);
        })
        .catch(error => {
            console.error('Error during AJAX request:', error);
        });
    }

    function redirectToUrlWithCSRF(url) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;

        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = csrfToken;
        form.appendChild(csrfInput);

        document.body.appendChild(form);
        form.submit();
    }
});