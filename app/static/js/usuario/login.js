  function togglePassword() {
    const input = document.getElementById("id_contraseña"); // Django genera id_contraseña
    const icon = document.querySelector(".toggle-password");

    if (input.type === "password") {
      input.type = "text";
      icon.classList.remove("fa-eye");
      icon.classList.add("fa-eye-slash");
    } else {
      input.type = "password";
      icon.classList.remove("fa-eye-slash");
      icon.classList.add("fa-eye");
    }
  }
