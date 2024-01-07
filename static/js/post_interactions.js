import { postInteractions } from './interactions.js';
import { showModalsOnClick } from './likers_modals.js';

const loadedPostsExists = document.getElementById("loaded-posts");
const newPostsExists = document.getElementById("new-posts");

if (loadedPostsExists) {
    const loadedPostsContainerId = "loaded-posts";
    postInteractions(loadedPostsContainerId);
    showModalsOnClick(loadedPostsContainerId);    
} else {
    console.log("Error: the targeted container id (loaded-posts) doesn't exist");
}

if (newPostsExists) {
    const newPostsContainerId = "new-posts";
    postInteractions(newPostsContainerId);
    showModalsOnClick(newPostsContainerId);
} else {
    console.log("Error: the targeted container id (new-posts) doesn't exist");
}
