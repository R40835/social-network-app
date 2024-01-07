document.addEventListener('DOMContentLoaded', function () {
    const container = document.querySelector('.infinite-container');

    if (container != null) {
        container.addEventListener('click', function (event) {
            const target = event.target;
         
            if (target.classList.contains('comment-interaction')) {
                const commentId = target.getAttribute("comment-id");
                const commentCancelButton = document.getElementById(`comment-cancel-button-${commentId}`);
                const commentDeleteButton = document.getElementById(`comment-delete-button-${commentId}`);
                const closeModalButton = document.getElementById(`close-modal-${commentId}`);
                const modal = document.getElementById(`comment-modal-${commentId}`);

                // open modal on click
                openModal();
                
                // Function to open the modal
                function openModal() {
                    modal.style.display = 'block';
                }
        
                // Function to close the modal
                function closeModal() {
                    modal.style.display = 'none';
                }
        
                // Event listeners
                closeModalButton.addEventListener('click', closeModal);
                commentCancelButton.addEventListener('click', closeModal);
        
                // Event listener for the "Cancel" button inside the modal
                commentCancelButton.addEventListener('click', function () {
                    closeModal();
                });
        
                // Event listener for the "Delete" button inside the modal
                commentDeleteButton.addEventListener('click', function () {
                    const deleteUrl = commentDeleteButton.getAttribute("data-url");
                    window.location.href = deleteUrl;
                });
            } 
        });
    } 
});
