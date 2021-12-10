
function validateLoginForm() {
    var email = document.getElementById("emailid").value;
    var password = document.getElementById("passwordid").value;
    if (email === "") {
        alert("Username must be filled out");
        return false;
    }
    if (email.indexOf("@") === -1) {
        alert("Email must be valid");
        return false;
    }
    if (email.indexOf(".") === -1) {
        alert("Email must be valid");
        return false;
    }
    if (password === "") {
        alert("Password must be filled out");
        return false;
    }

    // process login
    return true;
}

function login() {
    if (validateLoginForm()) {
        var email = document.getElementById("emailid").value;
        var password = document.getElementById("passwordid").value;
        var data = {
            "email": email,
            "password": password
        };
        var form = document.createElement('form');
        form.setAttribute('method', 'post');
        form.setAttribute('action', '/login');
        form.setAttribute('style', 'display:none');
        var input = document.createElement('input');
        input.setAttribute('type', 'hidden');
        form.innerHTML = '<input type="text" name="email" value="' + email + '">' +
            '<input type="text" name="password" value="' + password + '">';
        document.body.appendChild(form);
        form.submit();
    }
}

function validateRegisterForm() {
    var username = document.getElementById("emailid").value;
    var password = document.getElementById("passwordid").value;
    var password2 = document.getElementById("password2id").value;
    var email = document.getElementById("emailid").value;

    if (username == "" && password == "" && password2 == "" && email == "") {
        alert("Please fill in all fields");
        return false;
    }

    if (email === "") {
        alert("Email must be filled out");
        return false;
    }
    if (email.indexOf("@") === -1) {
        alert("Email must be valid");
        return false;
    }
    if (email.indexOf(".") === -1) {
        alert("Email must be valid");
        return false;
    }
    if (username === "") {
        alert("Username must be filled out");
        return false;
    }
    if (password === "" || password !== password2) {
        alert("Passwords must be filled out and the same...");
        return false;
    }

    return true;
}

function register() {
    if (validateRegisterForm()) {
        alert("Validation successful!");
        var username = document.getElementById("usernameid").value;
        var password = document.getElementById("passwordid").value;
        var email = document.getElementById("emailid").value;
        var data = {
            username: username,
            password: password,
            email: email
        };
        var form = document.createElement('form');
        form.setAttribute('method', 'post');
        form.setAttribute('action', '/register');
        form.setAttribute('id', 'registerform');
        form.setAttribute('style', 'display:none');
        var input = document.createElement('input');
        input.setAttribute('type', 'hidden');
        form.innerHTML = '<input type="text" name="username" value="' + username + '">' +
            '<input type="text" name="password" value="' + password + '">' +
            '<input type="text" name="email" value="' + email + '">';
        document.body.appendChild(form);
        form.submit();
    }
}