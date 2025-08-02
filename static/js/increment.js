document.addEventListener('DOMContentLoaded', function () {
  const decrementBtn = document.querySelector('.btn-decrement');
  const incrementBtn = document.querySelector('.btn-increment');
  const quantityInput = document.querySelector('input[name="quantity"]');

  decrementBtn?.replaceWith(decrementBtn.cloneNode(true));
  incrementBtn?.replaceWith(incrementBtn.cloneNode(true));

  const newDecrementBtn = document.querySelector('.btn-decrement');
  const newIncrementBtn = document.querySelector('.btn-increment');

  newDecrementBtn?.addEventListener('click', function () {
    let current = parseInt(quantityInput.value);
    if (current > 1) {
      quantityInput.value = current - 1;
    }
  });

  newIncrementBtn?.addEventListener('click', function () {
    let current = parseInt(quantityInput.value);
    quantityInput.value = current + 1;
  });
});
