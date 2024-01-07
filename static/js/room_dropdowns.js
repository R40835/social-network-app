document.addEventListener('DOMContentLoaded', function () {
    // Function to fetch member data
    function fetchMemberData(memberLink) {
        const memberId = memberLink.getAttribute('member-id');

        fetch('/chat/room-member/' + memberId + '/')
        .then(response => response.json())
        .then(data => {
            const userName = data.member_name;
            const profilePhoto = data.member_profile_photo;
            const imgElement = document.createElement('img');
            const memeberInfoDiv = document.createElement('div');
            const userNameElement = document.createElement('p');
            
            imgElement.src = profilePhoto;
            userNameElement.textContent = userName;
            imgElement.alt = 'Profile Photo';
            imgElement.style.width = '20px';
            imgElement.style.borderRadius = '50%';
            memeberInfoDiv.classList.add('box-user-container');
            userNameElement.style.marginLeft = '5px';

            memeberInfoDiv.appendChild(imgElement);
            memeberInfoDiv.appendChild(userNameElement);
            memberLink.appendChild(memeberInfoDiv);
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
    }

    // Function to handle the loading of new pages
    function handleNewPage() {
        const memberLinks = document.querySelectorAll('[id^="member-"]');

        memberLinks.forEach(function (memberLink) {
            fetchMemberData(memberLink);
        });
    }

    // Set up Waypoint for infinite scrolling
    var infinite = new Waypoint.Infinite({
        element: $('.infinite-container')[0],

        offset: 'bottom-in-view',

        onBeforePageLoad: function () {
            $('.loading').show();
        },
        onAfterPageLoad: function () {
            $('.loading').hide();
            handleNewPage();
        }
    });

    // Fetch member data for the initial page
    handleNewPage();
});






