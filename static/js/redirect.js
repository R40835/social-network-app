document.addEventListener('DOMContentLoaded', function() {
    const actionButtons = document.querySelectorAll('.message-button, .add-friend-button, .remove-friend-button, .comment-button');
    const csrfToken = getCookie('csrftoken');

    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.getAttribute('data-url');
            redirectToUrlWithCSRF(url);
        });
    });

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

    // Function to retrieve cookies
    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
    }
});
