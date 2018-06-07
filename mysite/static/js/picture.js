function startLoadingAnimation()
{
    //setInterval(blinker, 10000);
    // Showing the "loading animation":

    document.getElementById('loadingAnimation').style.visibility = 'visible';

    // Hiding the input fields:

    //document.getElementById("descriptionDiv").style.visibility = "hidden";

  // Posting the form:
  //document.getElementById("newItemForm").submit();
}


function reloadLastTakenImageFromDatabase() {
  var preview = document.querySelector('img');
  var oldImagePath = document.getElementById('value_');

  preview.src = oldImagePath.value;
  document.getElementById('userPicture').addEventListener('change', addPhoto);
}

function addPhoto() {
  var preview = document.querySelector('img');
  var file = document.querySelector('input[type=file]').files[0];
  var reader = new FileReader();
  reader.addEventListener("load", function() {
    preview.src = reader.result;
  }, false);
  if (file) {
    reader.readAsDataURL(file);
  }
  preview.src = "";

  // Feedbacks-controller knows that the input
  // has been given if value_ is not empty:
  document.getElementById('value_').value = 'X';
}
