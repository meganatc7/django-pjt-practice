const usernameField = document.querySelector('#username-field');
const feedBackArea = document.querySelector('#invalid-feedback');
const emailField = document.querySelector('#email-field');
const emailFeedBackArea = document.querySelector('#invalid-email');
const passwordField = document.querySelector('#password-field');
const usernameSuccessOutput = document.querySelector('.usernamesuccessOutput');
const showPasswordToggle = document.querySelector('#show-password');
const submitBtn = document.querySelector('.submit-btn');

const handleToggleInput = (e) => {

  if (showPasswordToggle.textContent === 'SHOW') {
    showPasswordToggle.textContent = 'HIDE';
    passwordField.setAttribute('type', 'text');
  } else {
    showPasswordToggle.textContent = 'SHOW';
    passwordField.setAttribute('type', 'password');
  }

}

showPasswordToggle.addEventListener('click', handleToggleInput);


emailField.addEventListener('input',(e) => {
  const emailVal = e.target.value;

  emailField.classList.remove('is-invalid');
  emailFeedBackArea.style.display = 'none';
  
  
  if(emailVal.length > 0) {
    fetch('/authentication/validate-email/',{
      body: JSON.stringify({ email: emailVal }),
      method: 'POST',
    })
    .then((res) => res.json())
    .then((data) => {
      console.log('data',data);
      if (data.email_error) {
        submitBtn.disabled = true;
        emailField.classList.add('is-invalid');
        emailFeedBackArea.style.display = 'block';
        emailFeedBackArea.innerHTML = `<p class="text-danger">${data.email_error}</p>`
      } else {
        submitBtn.removeAttribute('disabled');
      }
    })
  }
})

usernameField.addEventListener('keyup',(e) => {
  const usernameVal = e.target.value;

  usernameSuccessOutput.style.display = 'block'
  usernameSuccessOutput.textContent = `Checking ${usernameVal}`

  usernameField.classList.remove('is-invalid');
  feedBackArea.style.display = 'none';
  feedBackArea.innerHTML = '';
  
  if(usernameVal.length > 0) {
    fetch('/authentication/validate-username/',{
      body: JSON.stringify({ username: usernameVal }),
      method: 'POST',
    })
    .then(res => res.json())
    .then(data=>{
      console.log('data',data);
      usernameSuccessOutput.style.display = 'none';
      if (data.username_error) {
        usernameField.classList.add('is-invalid');
        feedBackArea.style.display = 'block';
        feedBackArea.innerHTML = `<p class="text-danger">${data.username_error}</p>`
        submitBtn.disabled = true;
      } else {
        submitBtn.removeAttribute('disabled');
      }
    })

  }
})