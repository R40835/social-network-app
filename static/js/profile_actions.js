document.addEventListener("DOMContentLoaded", function() {
    const profileDiv = document.getElementById('single-profile'); 
    const csrfToken = getCookie('csrftoken');

    if (profileDiv) {
        const buttons = profileDiv.querySelectorAll(".action-button");

        buttons.forEach(button => {
            button.addEventListener("click", function() {
                const url = this.getAttribute("data-url");
                const userId = this.getAttribute("user-id");
                const action = this.getAttribute("button-action");
                const userRelationship = document.getElementById(`user-relationship-${userId}`);

                if (this.classList.contains("message-button")) {

                    redirectToUrlWithCSRF(url);
                }
                else if (this.classList.contains("add-friend-button")) { 

                    if (action === "send-cancel") {
                        sendActionRequest(url);
                        this.textContent = "Cancel";
                        this.classList.remove("add-friend-button");
                        this.classList.add("remove-friend-button");

                        userRelationship.textContent = "Pending";
                        userRelationship.style.fontWeight = "bold";    
                    }
                    else if (action === "accept") {
                        sendActionRequest(url);
                        this.classList.remove("add-friend-button");
                        this.classList.add("remove-friend-button");
                        this.textContent = "Remove";

                        userRelationship.textContent = "Friends";
                        userRelationship.style.fontWeight = "bold";    

                        var appPath = basePath + `friend/remove-send-cancel-request/${userId}`;
                        this.setAttribute("data-url", appPath);
                        this.setAttribute("button-action", "send-cancel");

                        const declineButton = document.getElementById('decline-button');

                        if (declineButton && declineButton.classList.contains("remove-friend-button")) {
                            declineButton.remove();
                        }
                    }

                } else if (this.classList.contains("remove-friend-button")) {

                    sendActionRequest(url);
                    this.textContent = "Add Friend";
                    this.classList.remove("remove-friend-button");

                    userRelationship.textContent = "Stranger";
                    userRelationship.style.fontWeight = "bold";
    
                    if (action === "send-cancel") {
                        this.classList.add("add-friend-button");
                    }
                    else if (action === "remove") {
                        this.classList.add("add-friend-button");
                        var appPath = basePath + `friend/send-cancel-request/${userId}`;
                        this.setAttribute("data-url", appPath);
                        this.setAttribute("button-action", "send-cancel");
                    }
                    else if (action === "decline") {

                        this.classList.remove("remove-friend-button");
                        this.classList.add("add-friend-button");
                        this.textContent = "Add Friend";
                        var appPath = basePath + `friend/send-cancel-request/${userId}`;
                        this.setAttribute("data-url", appPath);
                        this.setAttribute("button-action", "send-cancel");

                        const acceptButton = document.getElementById('accept-button');

                        if (acceptButton && acceptButton.classList.contains("add-friend-button")) {
                            acceptButton.remove();
                        }
                    }
                    else { // catches accept buttons that tuns it to add/cancel
                        this.classList.add("add-friend-button");
                        var appPath = basePath + `friend/send-cancel-request/${userId}`;
                        this.textContent = "Add Friend";
                        this.setAttribute("data-url", appPath);
                    }
                }
            });
        });
    }

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