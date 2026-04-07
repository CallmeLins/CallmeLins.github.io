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
   * Controls mobile menu behavior in blog post articles.
   */
  if ($(".post").length) {
    if ($("#footer-post").length) {
      var lastScrollTop = 0;
      $(window).on("scroll", function() {
        var topDistance = $(window).scrollTop();

        if (topDistance > lastScrollTop) {
          $("#footer-post").hide();
        } else {
          $("#footer-post").show();
        }
        lastScrollTop = topDistance;

        $("#toc-footer").hide();
        $("#share-footer").hide();

        if (topDistance < 50) {
          $("#actions-footer > #top").hide();
        } else if (topDistance > 100) {
          $("#actions-footer > #top").show();
        }
      });
    }
  }
});
