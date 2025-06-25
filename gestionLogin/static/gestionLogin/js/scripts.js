function validarFormulario() {
    let pass1 = document.getElementById("password").value;
    let pass2 = document.getElementById("confirm_password").value;
    let errorMsg = document.getElementById("error_password");

    if (pass1 !== pass2) {
        errorMsg.innerText = "Las contraseñas no coinciden.";
        return false;
    } else {
        errorMsg.innerText = "";
        return true;
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const userTypeSelect = document.getElementById("user_type");
    const errorUserType = document.getElementById("error_user_type");

    form.addEventListener("submit", function (event) {
        if (userTypeSelect.value === "") {
            event.preventDefault(); // Evita que el formulario se envíe
            errorUserType.textContent = "Debes seleccionar un tipo de usuario.";
            errorUserType.style.color = "red";
        } else {
            errorUserType.textContent = "";
        }
    });
});