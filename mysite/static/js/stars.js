function reloadOldValue() {
  // if the user has already previously
  // given value, it is updated to the page:
  var oldValue = document.getElementById('oldValue');

  radiobtn = document.getElementById(oldValue.value + "-star");
  radiobtn.checked = true;
}
