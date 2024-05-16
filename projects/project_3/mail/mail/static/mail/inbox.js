document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', () => compose_email());

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email(email = null) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';


  if (email === null) {
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  } else {
    document.querySelector('#compose-recipients').value = email.sender;
    document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
    document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: ${email.body}`;
  }

  // Add event listner to submit button
  document.addEventListener('submit', (event) => {

    // Prevent default form submit behavior 
    event.preventDefault();
    // Get the form information

    const recipients = document.querySelector('#compose-recipients').value;
    const composeSubject = document.querySelector('#compose-subject').value;
    const composeBody = document.querySelector('#compose-body').value;
    

    // Client side validation
    if (recipients === '') {

      alert('At least one recipient required.');
    
    } else {

      // Make a post request to backend
      fetch('/emails', {
        method: 'POST',
        body: JSON.stringify({
          recipients: recipients,
          subject: composeSubject,
          body: composeBody
        })
      })
      .then(response => response.json())
      .then(result => {
        if (result.error) {
          alert(result.error);
        } else {
          // Redirect user to sent page
          load_mailbox('sent');
        }
      });
    }
  });
  
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  if (mailbox === 'inbox') {
    // TODO: make inbox 
    mailboxInbox();
  } else if (mailbox === 'sent') {
    // TODO: make sent
    mailboxSent();
  } else if (mailbox === 'archive') {
    // TODO: make archive
    mailboxArchive();
  } else {
    // TODO: Show error
  }
}


// Separate the fetching functionality

function mailboxInbox() {
  fetch('/emails/inbox')
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      const emailElement = document.createElement('div');
      emailElement.classList.add('email-container');

      if (email.read === true) {
        emailElement.classList.add('email-read-true');
      }

      emailElement.innerHTML = `
        <div id="email-container-information">
        <p>From: ${email.sender}</p>
        <p>Subject: ${email.subject ? email.subject : '(no subject)'}</p>
        <p>${email.timestamp}</p>
        </div>
        <button class="btn btn-sm btn-outline-primary archive-button">Archive</button>
      `;

      emailElement.addEventListener('click', (event) => {
        event.preventDefault();
        loadEmail(email.id);
      });

      emailElement.querySelector('.archive-button').addEventListener('click', (event) => {
        load_mailbox('inbox');
        event.stopPropagation();
        event.preventDefault();
        archiveUnarchive(email.id, true);
      });

      document.querySelector('#emails-view').append(emailElement);
    });
  })
}


function mailboxSent() {
  fetch('/emails/sent')
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      const emailElement = document.createElement('div');
      emailElement.classList.add('email-container');

      emailElement.innerHTML = `
        <p>Recipients: ${email.recipients}</p>
        <p>Subject: ${email.subject ? email.subject : '(no subject)'}</p>
        <p>${email.timestamp}</p>
      `;

      emailElement.addEventListener('click', (event) => {
        event.preventDefault();
        loadEmail(email.id);
      });

      document.querySelector('#emails-view').append(emailElement);
    });
  })
}


function mailboxArchive() {
  fetch('/emails/archive')
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {
      const emailElement = document.createElement('div');
      emailElement.classList.add('email-container');

      emailElement.innerHTML = `
        <p>From: ${email.recipients}</p>
        <p>Subject: ${email.subject ? email.subject : '(no subject)'}</p>
        <p>${email.timestamp}</p>
        <button class="btn btn-sm btn-outline-primary unarchive-button">Unarchive</button>
      `;

      emailElement.addEventListener('click', (event) => {
        event.preventDefault();
        loadEmail(email.id);
      });

      emailElement.querySelector('.unarchive-button').addEventListener('click', (event) => {
        load_mailbox('archive');
        event.stopPropagation();
        event.preventDefault();
        archiveUnarchive(email.id, false);

      });

      document.querySelector('#emails-view').append(emailElement);
    });
  })
}


function loadEmail(id) {
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
    emailView(email);
  });
}


function emailView(email) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#message').innerHTML = '';

  // display email view 
  document.querySelector('#email-view').style.display = 'block';

  // Fill out the email page with fetched data
  const user = document.querySelector('h2').innerHTML;

  document.querySelector('#subject-field').innerHTML = `<h3>${email.subject ? email.subject : '(no subject)'}</h3>`;
  document.querySelector('#sender-field').innerHTML = `From: ${email.sender}`;
  document.querySelector('#timestamp-field').innerHTML = email.timestamp;

  // Check multiple recipients
  if (user === email.recipients[0] && email.recipients.length === 1) {
    document.querySelector('#recipients-field').innerHTML = 'To me';
  } else if (user === email.recipients[0] && email.recipients.length > 1) {
    document.querySelector('#recipients-field').innerHTML = `To me and ${email.recipients.slice(1)}`;
  } else {
    document.querySelector('#recipients-field').innerHTML = `To: ${email.recipients}`;
  }
  
  document.querySelector('#body-field').innerHTML = email.body;

  // Change read status of email
  readUnread(email.id, true);
  
  document.querySelector('#unread-button').addEventListener('click', (event) => {
    event.preventDefault();
    readUnread(email.id, false);
    document.querySelector('#message').innerHTML = 'Marked as Unread';
  });

  document.querySelector('#reply-button').addEventListener('click', (event) => {
    event.preventDefault();
    compose_email(email);
  });
}


function readUnread(emailId, boolValue) {
  fetch(`/emails/${emailId}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: boolValue
    })
  })
}


function archiveUnarchive(emailId, boolValue) {
  fetch(`/emails/${emailId}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: boolValue
    })
  })
}