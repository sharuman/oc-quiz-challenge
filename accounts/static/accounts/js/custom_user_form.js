(function waitForDjangoJQuery() {
  if (typeof window.django !== "undefined" && typeof window.django.jQuery !== "undefined") {
    var $ = window.django.jQuery;

    function togglePasswordFields() {
      const userType = $('#id_user_type').val();
      console.log('User type:', userType); // DEBUG

      // For add form
      const password1Row = $('#id_password1').closest('.form-row');
      const password2Row = $('#id_password2').closest('.form-row');

      // For change form
      const passwordHashRow = $('#id_password').closest('.form-row');
      const changePasswordSection = $('fieldset.module.change-password-section');

      if (userType && userType.toLowerCase() === 'participant') {
        passwordHashRow.length && passwordHashRow.hide();
        changePasswordSection.length && changePasswordSection.hide();

        password1Row.length && password1Row.hide();
        password2Row.length && password2Row.hide();
      } else {
        passwordHashRow.length && passwordHashRow.show();
        changePasswordSection.length && changePasswordSection.show();

        password1Row.length && password1Row.show();
        password2Row.length && password2Row.show();
      }
    }

    $(function() {
      togglePasswordFields(); // On page load
      $('#id_user_type').on('change', togglePasswordFields); // On user type change
    });

  } else {
    // Try again shortly if django.jQuery isn't ready yet
    setTimeout(waitForDjangoJQuery, 50);
  }
})();
