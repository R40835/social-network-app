document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = getCookie('csrftoken');
    const like = document.querySelector('.like-button');
    const postId = like.getAttribute('data-post-id');

    const commentButton = document.querySelector(`.comment-button`);
    const likeButton = document.getElementById(`like-button-${postId}`);
    const unlikeButton = document.getElementById(`unlike-button-${postId}`);       

    commentButton.addEventListener('click', function() {
        const url = this.getAttribute('data-url');
        redirectToUrlWithCSRF(url);
    });

    likeButton.addEventListener('click', function() {
        const postId = this.getAttribute('data-post-id');
        const url = this.getAttribute('data-url');
        const isLiked = this.getAttribute('data-liked') === 'true';

        sendActionRequest(url, postId, isLiked);
    });

    unlikeButton.addEventListener('click', function() {
        const postId = this.getAttribute('data-post-id');
        const url = this.getAttribute('data-url');
        const isLiked = this.getAttribute('data-liked') === 'true';

        sendActionRequest(url, postId, isLiked);
    });

    function sendActionRequest(url, postId, isLiked) {
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
            console.log('Response from the server:', data);

            // Update like count in related elements
            updateLikeCount(postId, data.likes);

            // Toggle button state
            toggleButtonState(isLiked, postId);
        })
        .catch(error => {
            console.error('Error during AJAX request:', error);
        });
    }

    function toggleButtonState(showLike, postId) {
        const likeButton = document.querySelector(`#like-button-${postId}`);
        const unlikeButton = document.querySelector(`#unlike-button-${postId}`);

        if (showLike) {
            likeButton.style.display = 'block';
            unlikeButton.style.display = 'none';
        } else {
            likeButton.style.display = 'none';
            unlikeButton.style.display = 'block';
        }
    }

    function updateLikeCount(postId, newLikeCount) {
        const likeCountElements = document.querySelectorAll(`#likes-count-${postId}`);
        
        likeCountElements.forEach(element => {
            element.textContent = `${newLikeCount}`;
        });
    }

    function getCookie(name) {
        var value = "; " + document.cookie;
        var parts = value.split("; " + name + "=");
        if (parts.length == 2) return parts.pop().split(";").shift();
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