document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll('.add-to-wishlist').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const cardId = this.dataset.cardId;

      fetch(`/add_to_wishlist/${cardId}`, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(res => res.json())
      .then(data => {
        alert(data.message);
        const icon = this.querySelector('i');
        icon.classList.remove('text-secondary');
        icon.classList.add('text-danger');
      })
      .catch(() => alert("Failed to add to wishlist."));
    });
  });
});
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".buy-now-btn").forEach(button => {
    button.addEventListener("click", function () {
      const cardId = this.dataset.cardId;
      const formData = new FormData();
      formData.append("card_id", cardId);

      fetch("/add_to_cart", {
        method: "POST",
        body: formData
      }).then(() => {
        window.location.href = "/cart";
      });
    });
  });
});






