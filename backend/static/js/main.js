// Back to Top Button
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Dark Mode Toggle
function toggleDarkMode() {
  document.documentElement.classList.toggle('dark');
}

// Navbar Auto Hide on Scroll
let lastScrollTop = 0;
const navbar = document.getElementById("navbar");
if (navbar) {
  window.addEventListener("scroll", function () {
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    if (scrollTop > lastScrollTop) {
      navbar.classList.add("-translate-y-full");
    } else {
      navbar.classList.remove("-translate-y-full");
    }
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
  });
}

// Readme Toggle Functionality
function toggleReadme() {
  const content = document.getElementById("readmeContent");
  const preview = document.getElementById("readmePreview");

  if (content && preview) {
    const isHidden = content.classList.contains("hidden");

    content.classList.toggle("hidden");
    preview.classList.toggle("hidden");

    // Optional: Update an "aria-expanded" or toggle icon if needed
    const toggleBtn = document.getElementById("readmeToggleBtn");
    if (toggleBtn) {
      toggleBtn.setAttribute("aria-expanded", !isHidden);
    }
  }
}


// Swiper Slider Init (if needed on page)
if (document.querySelector(".mySwiper")) {
  new Swiper(".mySwiper", {
    loop: true,
    autoplay: {
      delay: 1500,
      disableOnInteraction: false,
      pauseOnMouseEnter: true
    },
    pagination: {
      el: ".swiper-pagination",
      clickable: true,
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
  });
}
// folder toggle
  function toggleFolderTree() {
    const tree = document.getElementById("folderTreeContent");
    tree.classList.toggle("hidden");
  }