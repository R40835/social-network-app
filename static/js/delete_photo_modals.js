document.addEventListener('DOMContentLoaded', function () {
    const container = document.querySelector('.infinite-container');

    if (container != null) {
        container.addEventListener('click', function (event) {
            const target = event.target;
         
            if (target.classList.contains('photo-interaction')) {
                const photoId = target.getAttribute("photo-id");
                const photoCancelButton = document.getElementById(`photo-cancel-button-${photoId}`);
                const photoDeleteButton = document.getElementById(`photo-delete-button-${photoId}`);
                const closeModalButton = document.getElementById(`close-modal-${photoId}`);
                const modal = document.getElementById(`photo-modal-${photoId}`);
                
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
                photoCancelButton.addEventListener('click', closeModal);
        
                // Event listener for the "Cancel" button inside the modal
                photoCancelButton.addEventListener('click', function () {
                    closeModal();
                });
        
                // Event listener for the "Delete" button inside the modal
                photoDeleteButton.addEventListener('click', function () {
                    const deleteUrl = photoDeleteButton.getAttribute("data-url"); 
                    window.location.href = deleteUrl;
                });
            } 
        });
    } 
});
