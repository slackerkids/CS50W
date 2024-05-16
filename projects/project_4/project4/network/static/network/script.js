const editButtons = document.querySelectorAll('.edit-button');

editButtons.forEach(button => {
  let state = 'edit';
  button.addEventListener('click', (event) => {
    event.preventDefault();

    if (state === 'edit') {
      editPost(button);
      state = 'save';
    } else if (state === 'save') {
      savePost(button);
      state = 'edit';
    }
  });
});

function editPost(button) {
  let post = document.querySelector(`#post-content-${button.dataset.postId}`);
  const postContent = post.innerHTML;
  post.innerHTML = `<textarea class="form-control" id="edit-textarea-post-id-${button.dataset.postId}">${postContent}</textarea>`;
  button.innerHTML = '<i class="fa-solid fa-check"></i>';
}

function savePost(button) {
  const updatedPost = document.querySelector(`#edit-textarea-post-id-${button.dataset.postId}`).value;
  let post = document.querySelector(`#post-content-${button.dataset.postId}`);
  post.innerHTML = updatedPost;
  button.innerHTML = '<i class="fa-solid fa-pen-to-square" style="color: #232323;"></i>';

  fetch('/edit_post', {
    method: 'PUT',
    body: JSON.stringify({
      post_id: button.dataset.postId,
      updated_content: updatedPost
    })
  })
  .then(response => response.json())
  .then(data => {
    let messageDiv = document.querySelector(`#post-message-${button.dataset.postId}`);
    messageDiv.classList = 'alert alert-primary';
    messageDiv.innerHTML = data.message;
    setTimeout(() => {
      messageDiv.classList = '';
      messageDiv.innerHTML = '';
    }, 3000);
  });
}


// Function to like button
const likeButton = document.querySelectorAll(".like-button");

likeButton.forEach(button => {
  button.addEventListener('click', (event) => {
    event.preventDefault();
    fetch('/like_unlike', {
      method: 'POST',
      body: JSON.stringify({
        post_id: button.dataset.postId
      })
    })
    .then(response => response.json())
    .then(data => {
      let count = document.querySelector(`#like-count-${button.dataset.postId}`).innerHTML;

      if (data.message === "Liked") {
        count++;
      } else {
        count--;
      }
      document.querySelector(`#like-count-${button.dataset.postId}`).innerHTML = count;
    });
  });
});