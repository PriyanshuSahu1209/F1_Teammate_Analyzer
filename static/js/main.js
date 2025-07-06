(function ($) {
  "use strict";

  // Smooth scroll to top if you ever add a back-to-top button
  $('.back-to-top').click(function () {
    $('html, body').animate({ scrollTop: 0 }, 800);
    return false;
  });

})(jQuery);
