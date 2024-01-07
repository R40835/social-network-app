export function showModalsOnClick(containerIdentifier) {
    document.addEventListener('DOMContentLoaded', function () {
        const container = document.getElementById(containerIdentifier);

        if (container) {
            container.addEventListener('click', function (event) {
                const target = event.target;
                console.log("DOMContentLoaded event fired");

                const postButton = target.closest('[post-likers-id]');

                if (postButton) {
                    const postId = postButton.getAttribute('post-likers-id');
                    const modal = document.querySelector(`#myModal-${postId}`);
                    const span = modal.querySelector(`#close-${postId}`);

                    modal.style.display = 'block';
                    event.stopPropagation();

                    // Load content from the specified URL
                    const url = postButton.getAttribute('data-url'); 
                    console.log(url);

                    fetch(url)
                        .then(response => response.text())
                        .then(data => {
                            document.getElementById(`likersContainer-${postId}`).innerHTML = data; 
                        })
                        .catch(error => {
                            console.error('Error loading content:', error); 
                        });

                    span.addEventListener('click', function (event) {
                        modal.style.display = 'none';
                        event.stopPropagation();
                    });
                }
            });

            window.addEventListener('click', function (event) {
                const modal = event.target.closest('.modal');

                if (modal) {
                    modal.style.display = 'none';
                }
            });
        }
    });
};
