document.addEventListener('DOMContentLoaded', function() {
    // Add an onclick event for each tile
    var tiles = document.querySelectorAll('.tile');
    tiles.forEach(function(tile) {
        tile.addEventListener('click', function() {
            // Get the data-url attribute from the clicked tile
            var url = tile.getAttribute('data-url');
            // Redirect to the specified URL
            window.location.href = url;
        });
    });
});