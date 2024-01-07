document.addEventListener('DOMContentLoaded', function () {
    
    const openModalButton = document.getElementById('account-open-modal-button');

    if (openModalButton != null) { 
        const closeModalButton = document.getElementById('close-modal');
        const accountCancelButton = document.getElementById('account-cancel-button');
        const accountDeleteButton = document.getElementById('account-delete-button');
        const modal = document.getElementById('account-modal');

        function openModal() {
            modal.style.display = 'block';
        }

        function closeModal() {
            modal.style.display = 'none';
        }

        openModalButton.addEventListener('click', openModal);
        closeModalButton.addEventListener('click', closeModal);
        accountCancelButton.addEventListener('click', closeModal);

        accountDeleteButton.addEventListener('click', function () {
            const deleteUrl = accountDeleteButton.getAttribute("data-url");
            window.location.href = deleteUrl;
        });

        accountDeleteButton.addEventListener('click', function () {
            closeModal();
        });
    }
});