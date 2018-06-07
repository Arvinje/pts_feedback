function reloadOldValue() {
  var oldValue = document.getElementById('oldValue');

  radiobtn = document.getElementById(oldValue.value);
  radiobtn.checked = true;
}
