var carousel = document.querySelector('.carousel-slides');
// We want there to be 4 videos visible in each 'slide' as such the number of slides is slides//4 -> this is not fool proof and needs a fix based on the window width and the length of the total carousel
var slides = carousel.querySelectorAll('iframe');
var carousel_length = slides.length / 4
var currentSlide = 0;

function showNextSlide() {
  if (currentSlide < carousel_length - 1) {
    currentSlide++;
  } else {
    currentSlide = 0;
  }
  carousel.style.transform = `translateX(-${currentSlide * 100}%)`;
}

function showPreviousSlide() {
  if (currentSlide > 0) {
    currentSlide--;
  } else {
    currentSlide = carousel_length - 1;
  }
  carousel.style.transform = `translateX(-${currentSlide * 100}%)`;
}

var nextButton = document.querySelector('.next-button');
var prevButton = document.querySelector('.prev-button');

nextButton.addEventListener('click', showNextSlide);
prevButton.addEventListener('click', showPreviousSlide);
