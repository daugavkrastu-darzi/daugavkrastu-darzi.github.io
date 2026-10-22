(() => {
  const button = document.querySelector('.nav-toggle');
  const navigation = document.querySelector('.primary-nav');
  if (!button || !navigation) return;

  button.addEventListener('click', () => {
    const open = button.getAttribute('aria-expanded') === 'true';
    button.setAttribute('aria-expanded', String(!open));
    navigation.classList.toggle('is-open', !open);
  });

  navigation.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
      button.setAttribute('aria-expanded', 'false');
      navigation.classList.remove('is-open');
    }
  });
})();
