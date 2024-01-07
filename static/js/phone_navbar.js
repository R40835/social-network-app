// toggle the visibility of the navbar
document.getElementById("mobileMenuToggle").addEventListener("click", function() {
    var navbarContent = document.querySelector(".navbar");
    navbarContent.classList.toggle("show");
});

// toggle the visibility of the collapse button
document.getElementById("collapseNavbarBtn").addEventListener("click", function() {
    var navbarContent = document.querySelector(".navbar");
    navbarContent.classList.remove("show");
});