// QuestionChoices are always stored as strings. Radio
// buttons use integers. That is why we need these functions

// If user has previously given a value for the question,
// this function retrieves it:
function setInitValueOnPageLoad()
{
  var radioButtonChoices = document.getElementsByName('usersChoice');
  var oldValue = document.getElementById('value_').value;

  // Values are stored to database as text. We need to search
  // for the radio button with same name
  for (var i = 0, length = radioButtonChoices.length; i < length; i++)
    if (radioButtonChoices[i].value == oldValue)
    {
      radioButtonChoices[i].checked = 1;

      oldValue = i;
      break;
    }
}

function setAnswerValue(userSelectedRadioButtonIndex)
{
  var radioButtonChoices = document.getElementsByName('usersChoice');
  document.getElementById('value_').value = radioButtonChoices[userSelectedRadioButtonIndex].value;
}
