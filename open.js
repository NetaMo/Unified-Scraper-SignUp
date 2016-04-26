/**
 * Created by dafnaarbiv on 18/04/2016.
 */
function getUserName() {
    var nameField = document.getElementById('nameField').value;
    var result = document.getElementById('result');

    if (nameField.length < 3) {
        result.textContent = 'Username must contain at least 3 characters';
        //alert('Username must contain at least 3 characters');
    } else {
        result.textContent = 'Your username is: ' + nameField;
        //alert(nameField);
    }
    jQuery.ajax({
        url: 'localhost:8888/userName',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({"userName":result.textContent}),
        type: 'POST',
        success: function(response) {
            console.log(response);
        },
        error: function(error) {
            console.log(error);
        }
    });
}