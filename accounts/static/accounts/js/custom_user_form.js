(function waitForDjangoJQuery() {
  if (typeof window.django !== "undefined" && typeof window.django.jQuery !== "undefined") {
    var $ = window.django.jQuery;

    function togglePasswordFields() {
      const userType = $('#id_user_type').val();
      console.log('User type:', userType); // DEBUG

      const passwordHashRow = $('#id_password').closest('.form-row');
      const changePasswordSection = $('fieldset.module.change-password-section');

      if (userType && userType.toLowerCase() === 'participant') {
        passwordHashRow.length && passwordHashRow.hide();
        changePasswordSection.length && changePasswordSection.hide();
        
      } else {
        passwordHashRow.length && passwordHashRow.show();
        changePasswordSection.length && changePasswordSection.show();
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
