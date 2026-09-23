// Fixture: supplied text is sent to a user-configured service.
async function translate(text) {
  return fetch("https://api.example.test/translate", {method:"POST", body:text});
}
