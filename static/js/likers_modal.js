// Get the modal and the button that opens it
const modal = document.getElementById("myModal");
const btn = document.getElementById("myBtn");

// Get the close button inside the modal
const closeBtn = modal.querySelector(".close");

// When the button is clicked, open the modal
btn.addEventListener("click", function () {
    modal.style.display = "block";

    // Load content from the specified URL 
    const url = btn.getAttribute('data-url');
    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.getElementById("likersContainer").innerHTML = data;
        })
        .catch(error => {
            console.error('Error loading content:', error);
        });
});

// When the close button is clicked, close the modal
closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
});

// When the user clicks outside the modal, close it
window.addEventListener("click", function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
});