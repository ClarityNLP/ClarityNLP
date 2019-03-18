$(document).ready(function() {
  var isLocal = true;
  $('.login-method-toggle').on('click', function() {
    isLocal = !isLocal;
    isLocal ? $(this).text('Log In via External Providers') : $(this).text('Log In via Local Account')
    $('.external-providers, .login-panel').toggleClass('hidden');
  });
});
