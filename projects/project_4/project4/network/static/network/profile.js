function updateCounts(userId) {
    fetch(`/follow_unfollow_count/${userId}`)
        .then(response => response.json())
        .then(data => {
            document.querySelector('#followersCount').innerHTML = `${data.followers_count} following`;
            document.querySelector('#followedCount').innerHTML = `${data.followed_count} followers`;
        });
}

document.querySelector("#followUnfollowButton").addEventListener("click", event => {
    event.preventDefault();

    const userId = document.querySelector("#followUnfollowButton").dataset.userId;
    const button = document.querySelector("#followUnfollowButton");

    let newText;
    if (button.innerHTML === 'Follow') {
        newText = "Unfollow";
        button.classList.remove("btn-primary");
        button.classList.add("btn-danger");
    } else {
        newText = "Follow";
        button.classList.remove("btn-danger");
        button.classList.add("btn-primary");
    }

    button.innerHTML = newText;

    fetch(`/follow_unfollow/${userId}`, {
        method: 'POST'
    }) 
    .then(response => response.json())
    .then(data => {
        console.log(data.message);
        updateCounts(userId);
    });
});
