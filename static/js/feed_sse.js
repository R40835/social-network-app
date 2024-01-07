let firstNewPost = true;

document.addEventListener('DOMContentLoaded', function () {
    var ssePath = basePath + "sse/feed/";
    const eventSource = new EventSource(ssePath);

    eventSource.onopen = function(event) {
        console.log("FEED SSE connection opened");
    }
    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);

        console.log('Received message:', data);
        const newData = data.is_new;

        // Keeping post data only
        delete data.is_new;

        // Add new post dynamically only if user is on the feed
        const currentPath = window.location.pathname;
        
        if (currentPath === "/post/feed/") {
            if (newData) {
                const NewPostsContainer = document.getElementById("new-posts");
                const currentUserId = NewPostsContainer.getAttribute("current-user-id");
                
                for (const post in data) {
                    const postExists = document.getElementById(`${data[post].post_id}`);
                    // Not adding posts uploaded by current user as the latter is 
                    // being redirected. This is in order to avoid duplicate posts.
                    if (data[post].user_id != currentUserId && !postExists) {
                        // Post data from server
                        const postId = data[post].post_id;
                        const userId = data[post].user_id;
                        const postDescription = data[post].description;
                        const postPhoto = data[post].photo;
                        const postLikes = data[post].likes;
                        const postComments = data[post].comments;
                        const postDateCreated = data[post].date_created;
                        const userName = data[post].name;
                        const userProfilePhoto = data[post].profile_photo;    
                
                        // Adding new post to the UI    
                        // Post container
                        const boxContainerElement = document.createElement("div");
                        boxContainerElement.classList.add("box-container");
    
                        // Post box
                        const boxElement = document.createElement("div");
                        boxElement.classList.add("box");
    
                        // User profile
                        const userProfileLinkElement = document.createElement("a");
                        userProfileLinkElement.href = `/users/user-posts/${userId}`;
                        userProfileLinkElement.classList.add("custom-link");
                        
                        const userContainerElement = document.createElement("div");
                        userContainerElement.classList.add("box-user-container");
                        const userPhotoSrc = userProfilePhoto != null ? userProfilePhoto: "media/app/default-user.png";
                
                        const userPhotoElement = document.createElement("img");
                        userPhotoElement.classList.add("mini-profile-picture");
                        userPhotoElement.src = userPhotoSrc;
                        userPhotoElement.alt = "Profile Photo";
            
                        const userNameElement = document.createElement("p");
                        userNameElement.classList.add("user-name");
                        userNameElement.textContent = `${userName}`;
            
                        userContainerElement.appendChild(userPhotoElement);
                        userContainerElement.appendChild(userNameElement);
                        userProfileLinkElement.appendChild(userContainerElement);
                        
                        // Post description and photo
                        const PostLinkElement = document.createElement("a");
                        PostLinkElement.href = `/post/post/${postId}`;
                        PostLinkElement.classList.add("custom-link");
            
                        const postDescriptionText = postDescription != null ? postDescription: null;
                        const postPhotoSrc = postPhoto != null ? postPhoto: null;                
                        
                        // Post details; likes, likers modal, and comments
                        const detailsElement = document.createElement("div");
                        detailsElement.id = "details";
                        
                        // Post likes
                        const likesLinkElement = document.createElement("a");
                        likesLinkElement.id = `myBtn-${postId}`;
                        likesLinkElement.classList.add("custom-link-likes");
                        likesLinkElement.setAttribute("post-likers-id", `${postId}`);
                        likesLinkElement.setAttribute("data-url", `/post/likers/${postId}`);
            
                        const likesIconElement = document.createElement("i");
                        likesIconElement.innerHTML = `<i class="fa-regular fa-thumbs-up"></i> `;
                        
                        const likesCountElement = document.createElement("span");
                        likesCountElement.id = `likes-count-${postId}`;
                        likesCountElement.textContent = ` ${postLikes}`;
            
                        likesLinkElement.appendChild(likesIconElement);
                        likesLinkElement.appendChild(likesCountElement);
            
                        // Likers modal
                        const modalElement = document.createElement("div");
                        modalElement.id = `myModal-${postId}`;
                        modalElement.classList.add("modal");
            
                        const modalContentElement = document.createElement("div");
                        modalContentElement.classList.add("modal-content");
            
                        const closeModalElement = document.createElement("span");
                        closeModalElement.classList.add("close");
                        closeModalElement.id = `close-${postId}`;
                        closeModalElement.innerHTML = "&times;";
            
                        const likersContainerElement = document.createElement("div");
                        likersContainerElement.id = `likersContainer-${postId}`;
    
                        modalContentElement.appendChild(closeModalElement);
                        modalContentElement.appendChild(likersContainerElement);
                        modalElement.appendChild(modalContentElement);
    
                        // Post comments
                        const commentsLinkElement = document.createElement("a");
                        commentsLinkElement.classList.add("custom-link-likes");
                        commentsLinkElement.href = `/post/post/${postId}`;
                        
                        const commentsIconElement = document.createElement("i");
                        commentsIconElement.innerHTML = `<i class="fa-regular fa-comment"></i> `;
                        const commentsCountElement = document.createElement("span");
                        commentsCountElement.textContent = `${postComments}`;
            
                        commentsLinkElement.appendChild(commentsIconElement);
                        commentsLinkElement.appendChild(commentsCountElement);
                        
                        detailsElement.appendChild(likesLinkElement);
                        detailsElement.appendChild(modalElement);
                        detailsElement.appendChild(commentsLinkElement);
    
                        // Post interaction buttons
                        const buttonsContainerElement = document.createElement("div");
                        buttonsContainerElement.classList.add("action-buttons");
            
                        const likeButtonElement = document.createElement("button");
                        likeButtonElement.classList.add("action-button", "like-button");
                        likeButtonElement.id = `like-button-${postId}`;
                        likeButtonElement.setAttribute("data-post-id", `${postId}`);
                        likeButtonElement.setAttribute("data-url", `/post/like-post/${postId}`);
                        likeButtonElement.setAttribute("data-liked", "false");
                        likeButtonElement.textContent = "like";
            
                        const unlikeButtonElement = document.createElement("button");
                        unlikeButtonElement.classList.add("action-button", "unlike-button");
                        unlikeButtonElement.id = `unlike-button-${postId}`;
                        unlikeButtonElement.style.display = "none";
                        unlikeButtonElement.setAttribute("data-post-id", `${postId}`);
                        unlikeButtonElement.setAttribute("data-url", `/post/unlike-post/${postId}`);
                        unlikeButtonElement.setAttribute("data-liked", "true");
                        unlikeButtonElement.textContent = "unlike";
            
                        const commentButtonElement = document.createElement("button");
                        commentButtonElement.classList.add("action-button", "comment-button");
                        commentButtonElement.setAttribute("data-post-id", `${postId}`);
                        commentButtonElement.setAttribute("data-url", `/post/create-comment/${postId}`);
                        commentButtonElement.textContent = "comment";
            
                        buttonsContainerElement.appendChild(likeButtonElement);
                        buttonsContainerElement.appendChild(unlikeButtonElement);
                        buttonsContainerElement.appendChild(commentButtonElement);
                        
                        // Date created 
                        const dateCreatedElement = document.createElement("small");
                        dateCreatedElement.classList.add("date");
                        const dateIndicatorElement = document.createElement("b");
                        dateIndicatorElement.textContent = "Date Created:";
            
                        const dateText = document.createTextNode(` ${postDateCreated}`);
            
                        dateCreatedElement.appendChild(dateIndicatorElement)
                        dateCreatedElement.appendChild(dateText);
                
                        // Adding elements to the UI
                        boxElement.appendChild(userProfileLinkElement);
                        const lineBreak1 = document.createElement("br");
                        boxElement.appendChild(lineBreak1);
                        
                        if (postDescriptionText){
                            const postDescriptionElement = document.createElement("p");
                            postDescriptionElement.textContent = postDescription;
            
                            PostLinkElement.appendChild(postDescriptionElement);
                        }
            
                        if (postPhotoSrc) {
                            const postPhotoElement = document.createElement("img");
                            postPhotoElement.classList.add("post-img");
                            postPhotoElement.src = postPhotoSrc;
                            postPhotoElement.alt = "Post Photo";
            
                            PostLinkElement.appendChild(postPhotoElement);
                        }
            
                        boxElement.appendChild(PostLinkElement);
            
                        const lineBreak2 = document.createElement("br");
    
                        boxElement.appendChild(lineBreak2);
                        boxElement.appendChild(detailsElement);
                        boxElement.appendChild(buttonsContainerElement);
    
                        const hr = document.createElement("hr");
    
                        boxElement.appendChild(hr);
                        boxElement.appendChild(dateCreatedElement);
                        
                        if (firstNewPost) {
                            const lineBreak4 = document.createElement("br");
                            NewPostsContainer.appendChild(lineBreak4);
    
                            const newPostsIndicator = document.getElementById("new-posts-indicator");
                            newPostsIndicator.style.display = 'block';
                            firstNewPost = false;
                        }

                        boxContainerElement.appendChild(boxElement)
                        NewPostsContainer.appendChild(boxContainerElement);                              
                    }
                }
            }    
        }
    };
});