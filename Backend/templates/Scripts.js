// Hamburger toggle
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');

hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('active');
  hamburger.classList.toggle('open');
});

// Hamburger animation
hamburger.addEventListener('click', () => {
  const spans = hamburger.querySelectorAll('span');
  spans[0].classList.toggle('rotate1');
  spans[1].classList.toggle('fade');
  spans[2].classList.toggle('rotate2');
});
