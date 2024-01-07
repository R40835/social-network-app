const fileInput = document.getElementById("{{form.photo.id_for_label}}");
const clearButton = document.getElementById("clear-button");
const fileInfo = document.getElementById("file-info");
// Handle file input change
fileInput.addEventListener("change", function () {
const file = fileInput.files[0]; // Get the selected file
if (file) {
    fileInfo.textContent = `Photo uploaded: ${file.name}`; // Display file name
    clearButton.style.display = "inline"; // Show the clear button
} else {
    fileInfo.textContent = "";
    clearButton.style.display = "none"; // Hide the clear button to avoid conflict with django from
}
});
// Handle clear button click
clearButton.addEventListener("click", function () {
    fileInput.value = null; // Clear the file input
    fileInfo.textContent = "";
    clearButton.style.display = "none"; // Hide the clear button
});