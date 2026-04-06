/**
 * Sets up Justified Gallery.
 */
if (!!$.prototype.justifiedGallery) {
  var options = {
    rowHeight: 140,
    margins: 4,
    lastRow: "justify"
  };
  $(".article-gallery").justifiedGallery(options);
}

function setupThemeToggle() {
  var config = window.CACTUS_THEME;
  if (!config) {
    return;
  }

  var stylesheet = document.getElementById("theme-stylesheet");
  var toggles = document.querySelectorAll("[data-theme-toggle]");
  var labels = document.querySelectorAll("[data-theme-toggle-label]");

  function normalizeTheme(theme) {
    return config.schemes.indexOf(theme) === -1 ? config.defaultScheme : theme;
  }

  function setTheme(theme) {
    var currentTheme = normalizeTheme(theme);
    document.documentElement.setAttribute("data-theme", currentTheme);
    if (stylesheet) {
      stylesheet.href = config.cssBase + currentTheme + ".css";
    }
    try {
      localStorage.setItem(config.storageKey, currentTheme);
    } catch (error) {}

    var label = config.labels[currentTheme] || currentTheme;
    labels.forEach(function(node) {
      node.textContent = label;
    });
    toggles.forEach(function(toggle) {
      toggle.setAttribute("title", config.toggleLabel + ": " + label);
      toggle.setAttribute("aria-label", config.toggleLabel + ": " + label);
    });
  }

  function nextTheme() {
    var currentTheme = normalizeTheme(document.documentElement.getAttribute("data-theme"));
    var currentIndex = config.schemes.indexOf(currentTheme);
    return config.schemes[(currentIndex + 1) % config.schemes.length];
  }

  toggles.forEach(function(toggle) {
    toggle.addEventListener("click", function(event) {
      event.preventDefault();
      setTheme(nextTheme());
    });
  });

  setTheme(document.documentElement.getAttribute("data-theme"));
}

$(document).ready(function() {
  setupThemeToggle();


  /**
   * Controls the different versions of  the menu in blog post articles 
   * for Desktop, tablet and mobile.
   */
  if ($(".post").length) {
    var menu = $("#menu");
    var nav = $("#menu > #nav");
    var menuIcon = $("#menu-icon, #menu-icon-tablet");

    /**
     * Display the menu on hi-res laptops and desktops.
     */
    if ($(document).width() >= 1440) {
      menu.show();
      menuIcon.addClass("active");
    }

    /**
     * Display the menu if the menu icon is clicked.
     */
    menuIcon.click(function() {
      if (menu.is(":hidden")) {
        menu.show();
        menuIcon.addClass("active");
      } else {
        menu.hide();
        menuIcon.removeClass("active");
      }
      return false;
    });

    /**
     * Add a scroll listener to the menu to hide/show the navigation links.
     */
    if (menu.length) {
      $(window).on("scroll", function() {
        var topDistance = menu.offset().top;

        // hide only the navigation links on desktop
        if (!nav.is(":visible") && topDistance < 50) {
          nav.show();
        } else if (nav.is(":visible") && topDistance > 100) {
          nav.hide();
        }

        // on tablet, hide the navigation icon as well and show a "scroll to top
        // icon" instead
        if ( ! $( "#menu-icon" ).is(":visible") && topDistance < 50 ) {
          $("#menu-icon-tablet").show();
          $("#top-icon-tablet").hide();
        } else if (! $( "#menu-icon" ).is(":visible") && topDistance > 100) {
          $("#menu-icon-tablet").hide();
          $("#top-icon-tablet").show();
        }
      });
    }

    /**
     * Show mobile navigation menu after scrolling upwards,
     * hide it again after scrolling downwards.
     */
    if ($( "#footer-post").length) {
      var lastScrollTop = 0;
      $(window).on("scroll", function() {
        var topDistance = $(window).scrollTop();

        if (topDistance > lastScrollTop){
          // downscroll -> show menu
          $("#footer-post").hide();
        } else {
          // upscroll -> hide menu
          $("#footer-post").show();
        }
        lastScrollTop = topDistance;

        // close all submenu"s on scroll
        $("#nav-footer").hide();
        $("#toc-footer").hide();
        $("#share-footer").hide();

        // show a "navigation" icon when close to the top of the page, 
        // otherwise show a "scroll to the top" icon
        if (topDistance < 50) {
          $("#actions-footer > #top").hide();
        } else if (topDistance > 100) {
          $("#actions-footer > #top").show();
        }
      });
    }
  }
});
