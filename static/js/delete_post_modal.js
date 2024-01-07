document.addEventListener('DOMContentLoaded', function () {
    
    const openModalButton = document.getElementById('post-open-modal-button');

    // Evaluates to true only when the user is the post author
    if (openModalButton != null) { 
        const closeModalButton = document.getElementById('close-modal');
        const postCancelButton = document.getElementById('post-cancel-button');
        const postDeleteButton = document.getElementById('post-delete-button');
        const modal = document.getElementById('post-modal');

        // Function to open the modal
        function openModal() {
            modal.style.display = 'block';
        }

        // Function to close the modal
        function closeModal() {
            modal.style.display = 'none';
        }

        // Event listeners
        openModalButton.addEventListener('click', openModal);
        closeModalButton.addEventListener('click', closeModal);
        postCancelButton.addEventListener('click', closeModal);

        // Set the delete link href when the modal is opened
        postDeleteButton.addEventListener('click', function () {
            const deleteUrl = postDeleteButton.getAttribute("data-url");
            window.location.href = deleteUrl;
        });

        postDeleteButton.addEventListener('click', function () {
            closeModal();
        });
    }
});